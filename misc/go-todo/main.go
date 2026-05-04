package main

import (
	"database/sql"
	"errors"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	_ "modernc.org/sqlite"
)

type Todo struct {
	ID        int64     `json:"id"`
	Title     string    `json:"title"`
	Done      bool      `json:"done"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type CreateTodoReq struct {
	Title string `json:"title"`
}

type UpdateTodoReq struct {
	Title *string `json:"title"`
	Done  *bool   `json:"done"`
}

var db *sql.DB

func main() {
	dbPath := os.Getenv("TODO_DB")
	if dbPath == "" {
		dbPath = "todo.db"
	}

	var err error
	db, err = sql.Open("sqlite", dbPath+"?_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	if err := initSchema(); err != nil {
		log.Fatal(err)
	}

	e := echo.New()
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	e.GET("/healthz", func(c echo.Context) error {
		return c.String(http.StatusOK, "ok")
	})

	e.GET("/todos", listTodos)
	e.POST("/todos", createTodo)
	e.GET("/todos/:id", getTodo)
	e.PUT("/todos/:id", updateTodo)
	e.DELETE("/todos/:id", deleteTodo)

	addr := os.Getenv("LISTEN_ADDR")
	if addr == "" {
		addr = ":8080"
	}
	e.Logger.Fatal(e.Start(addr))
}

func initSchema() error {
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS todos (
			id         INTEGER PRIMARY KEY AUTOINCREMENT,
			title      TEXT NOT NULL,
			done       INTEGER NOT NULL DEFAULT 0,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
		);
	`)
	return err
}

func listTodos(c echo.Context) error {
	rows, err := db.QueryContext(c.Request().Context(),
		`SELECT id, title, done, created_at, updated_at FROM todos ORDER BY id DESC`)
	if err != nil {
		return err
	}
	defer rows.Close()

	todos := make([]Todo, 0, 32)
	for rows.Next() {
		var t Todo
		var done int
		if err := rows.Scan(&t.ID, &t.Title, &done, &t.CreatedAt, &t.UpdatedAt); err != nil {
			return err
		}
		t.Done = done != 0
		todos = append(todos, t)
	}
	if err := rows.Err(); err != nil {
		return err
	}
	return c.JSON(http.StatusOK, todos)
}

func createTodo(c echo.Context) error {
	var req CreateTodoReq
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid body")
	}
	if req.Title == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "title is required")
	}

	res, err := db.ExecContext(c.Request().Context(),
		`INSERT INTO todos (title) VALUES (?)`, req.Title)
	if err != nil {
		return err
	}
	id, err := res.LastInsertId()
	if err != nil {
		return err
	}
	t, err := fetchTodo(c, id)
	if err != nil {
		return err
	}
	return c.JSON(http.StatusCreated, t)
}

func getTodo(c echo.Context) error {
	id, err := parseID(c)
	if err != nil {
		return err
	}
	t, err := fetchTodo(c, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return echo.NewHTTPError(http.StatusNotFound, "not found")
		}
		return err
	}
	return c.JSON(http.StatusOK, t)
}

func updateTodo(c echo.Context) error {
	id, err := parseID(c)
	if err != nil {
		return err
	}
	var req UpdateTodoReq
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid body")
	}

	current, err := fetchTodo(c, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return echo.NewHTTPError(http.StatusNotFound, "not found")
		}
		return err
	}
	if req.Title != nil {
		current.Title = *req.Title
	}
	if req.Done != nil {
		current.Done = *req.Done
	}

	done := 0
	if current.Done {
		done = 1
	}
	if _, err := db.ExecContext(c.Request().Context(),
		`UPDATE todos SET title = ?, done = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
		current.Title, done, id); err != nil {
		return err
	}

	t, err := fetchTodo(c, id)
	if err != nil {
		return err
	}
	return c.JSON(http.StatusOK, t)
}

func deleteTodo(c echo.Context) error {
	id, err := parseID(c)
	if err != nil {
		return err
	}
	res, err := db.ExecContext(c.Request().Context(),
		`DELETE FROM todos WHERE id = ?`, id)
	if err != nil {
		return err
	}
	affected, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if affected == 0 {
		return echo.NewHTTPError(http.StatusNotFound, "not found")
	}
	return c.NoContent(http.StatusNoContent)
}

func fetchTodo(c echo.Context, id int64) (*Todo, error) {
	row := db.QueryRowContext(c.Request().Context(),
		`SELECT id, title, done, created_at, updated_at FROM todos WHERE id = ?`, id)
	var t Todo
	var done int
	if err := row.Scan(&t.ID, &t.Title, &done, &t.CreatedAt, &t.UpdatedAt); err != nil {
		return nil, err
	}
	t.Done = done != 0
	return &t, nil
}

func parseID(c echo.Context) (int64, error) {
	s := c.Param("id")
	id, err := strconv.ParseInt(s, 10, 64)
	if err != nil || id <= 0 {
		return 0, echo.NewHTTPError(http.StatusBadRequest, "invalid id")
	}
	return id, nil
}

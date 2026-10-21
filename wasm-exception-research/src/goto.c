int goto_sum(int n) {
  int total = 0;
again:
  if (n <= 0) goto done;
  total += n;
  --n;
  goto again;
done:
  return total;
}

---
marp: true
theme: kaigi-on-rails-2026
paginate: true
size: 16:9
---

<!-- _class: cover -->
<!-- _paginate: false -->

---

<!-- _class: title -->
<!-- _paginate: false -->

# Zen and the Art of<br>File Upload Maintenance

## An Inquiry into Legacies

<i>Presentation by Uchio Kondo</i>

---

<!-- _class: section -->

# The Beginning<br>(of Your Web Development)

---

<!-- _class: body -->

- In 200X, you built your first blog app in Rails.
- A title and a body showed up on the screen.

---

<!-- _class: body -->

- What do you want to do next...?

---

<!-- _class: body -->

- Right — **file upload**.

---

<!-- _class: section -->

# Rails and File Upload

---

# What is File upload

- File upload is one of the most basic requirements of a web service.
- Ruby on Rails supports it, of course.
- That's **ActiveStorage**.

---

# B.A. (Before ActiveStorage)

- But until ActiveStorage arrived, no rails had been laid for files.
- A short history and tour of the libraries.

---

<!-- _class: section -->

# The Situation at SmartHR

---
<!--
_footer: aaa
-->
# When something is done

- The HR/labor management application at SmartHR got its first commit around 2015.
- A world before ActiveStorage.

---

# The choice

- So we had to pick a gem. That gem was CarrierWave.
- And then, ten years went by.

---

# Smell of the legacy

- We ran CarrierWave for almost ten years, and slowly what we wanted drifted away from what the gem could do.
- One of them: how badly it fit the data model at the core of our product — the bitemporal data model.

---

# In a bitemporal data model...

- Data is never deleted. So files should not be deleted either.
- We have to control CarrierWave's habit of deleting the file on destroy.

---

# In a bitemporal data model...

- A "history" holding the same image can get split.
- Which, in an unlucky combination, made the upload run all over again.

---

<!-- _class: section-plain -->

# On top of that, several problems came up

---

# Path resolution kept getting more complex

- It was complex enough that it broke, easily, again and again.
- And when we tried to change it years later, backward compatibility forced dirty time-based if statements on us.

---

# Synchronous generation of resized variants

- CarrierWave can generate resized versions of an image

```ruby
version :large, ...
```

- Some models declare several versions, and generate every one of them synchronously

---

# EXIF handling

- Inside CarrierWave, we process the image's EXIF data on upload
    - Rotation
    - Stripping location and other personal data
- What the spec should be was never clear, and it cost us performance

---

# Bi-temporal model restriction

- Combine a "history split" with synchronous variant generation, and a single update could fire an absurd number of uploads.
- On top of that, piling complex responsibilities onto the uploader meant we could no longer read what an update would touch.

---

<!-- _class: section-plain -->

# All of it tangled together into debt.

---

<!-- _class: section -->

# Untangling the Problem

---

<!-- _class: body -->

- So what do we do?
- Our team took the approach of untangling the responsibilities.

---

# What we did about path resolution

- Work to pin down the cache path and the persisted path
- A quick word on the lifecycle

---

# Synchronous generation of resized variants

- Extracted a service that generates the variants reactively

---

# EXIF handling

- Dropped the rotation we never needed, moved the stripping off the request

---

<!-- _class: section-plain -->

# Simplify the spec, take off the model what it should never have carried

---

# By the way, what about bi-temporals and performance?

- We added a path that skips the upload when a "history split" happens.
- It can only be hacky code built on CurrentAttributes, but it holds for now.
- This one adds complexity, so we are torn. A stopgap, with replacement in mind.

---

<!-- _class: section -->

# The Future of File Upload

---

# The ideal and the reality


- In the end, we should also ask whether to drop CarrierWave.
- First: now that the responsibilities are untangled, an upgrade is at least on the table.
- Still, how it fits our history model is as bad as ever.

---

<!-- _class: section-plain -->

# And if we leave, where do we go?

---

# ActiveStorage?

- It needs a join to associate with a model, and in our tables one model often points at five or six images. Performance looks rough. Not a straightforward move.

---

# Another library, like Shrine?

- Shrine actually has no official GCS support.
- Plugin-based, every step loosely coupled — that is strong. But it also means building a lot in-house.

---

# Our own library...?

- Given how it tangles with history, and the rise of AI, maybe this is an option we should not throw out after all.

---

<!-- _class: section -->

# Conclusion

---

# For all Rails developers who struggle

- Honestly, we have not reached a conclusion yet.
- But I have told you one story, hoping it gives programmers fighting the same fight something to think with.


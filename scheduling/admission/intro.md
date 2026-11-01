# The harbor gate

After the API server checks **who** you are (authentication) and **what** you may do (authorization),
every request passes the **admission** gate: plugins that can **change** it (mutating) or **refuse** it (validating).

You'll switch a plugin on by editing the API server's static pod manifest, like in the exam.
⚠️ A typo here stops the API server: make a backup first!

Lessons: [2.14 Admission controllers](https://captains-academy.site/course/kubernetes/lesson/2.14) · [2.15 Validating vs mutating webhooks](https://captains-academy.site/course/kubernetes/lesson/2.15)

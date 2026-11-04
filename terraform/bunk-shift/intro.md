# The bunk shift

In `/root/bunks`, one `local_file.bunk` per crew member is built with **count**: `bunk[0]`, `bunk[1]`, `bunk[2]`.
Bo is leaving at the next port.

See the problem first (this changes nothing):
```
cd /root/bunks
terraform plan -var 'crew=["Ada","Cyrus"]'
```
One person leaves, and two bunks change. 😬

Lessons: [6.3 count](https://captains-academy.site/course/terraform/lesson/6.3) · [6.4 for_each](https://captains-academy.site/course/terraform/lesson/6.4)

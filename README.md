# vot iz zrunner

its a python utility to manage the running zrok sessions to serve the websites. it is to ensure that the zrok sessions dont stop, and if they do, get them back up online.

although that is the usecase, this is more general purpose and can be used to keep any service running over time, and periodically check if they are running normally.

## todo

- [x] project name
- [x] setup git
- [x] python check running services in os
- [x] create table in sqlite db for each service
- [x] read latest from table
- [x] insert row into table
- [x] execute a command in background
- [x] get pid and entry in table
- [ ] needs extensive testing to see that pid + 1 is that of the executed command since pid belongs to the spawned shell
- [ ] create a multi-core test to check this out
- [ ] test each service to see if they're running
- [ ] restart them if they need to be restarted
- [ ] entry to db
- [ ] check internet connectivity
- [ ] forgo current execution if no internet, or sleep for 5 mins?
- [ ] logging
- [ ] tests
- [ ] cron
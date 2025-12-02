#3. After some months you are contacted by the same canned company to make some modifications to the system you developed before:
#a. Create a ‘Supervisor’ user.
#b. Add that user to the ‘Distribution’ group.
#c. Modify the ‘Designed Tasks’ folder owner to be Supervisor.
#d. Modify the permissions of the ‘Designed tasks’ folder. The
#‘Distribution’ group must have read, write, and execute permission

sudo adduser Supervisor
sudo usermod -aG Distribution Supervisor

sudo chown -R Supervisor "Designed tasks"

sudo chmod -R 770 "Designed tasks"
sudo chgrp -R Distribution "Designed tasks"


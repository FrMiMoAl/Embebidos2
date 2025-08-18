#Using the previous exercise is required to make a route tree with the following features:
#a. Create a main folder called ‘Designed tasks’.

mkdir "Designed_task"

#b. Inside that folder the directories: ‘Maintenance’, ‘Production Line’‘Fixes’ and ‘Costs’ must be created.
mkdir "Designed_task"/{"Maintenance","Production_line","Fixes","Costs"}

#c. Each folder must have a file called ‘dates’ which contains specific workers schedules according to their roles. You can select the schedule for each role.
touch "Designed_task"/"Maintenance"/dates
touch "Designed_task"/"Production_line"/dates
touch "Designed_task"/"Fixes"/dates
touch "Designed_task"/"Costs"/dates

#d. Add a file to the ‘Designed tasks’ folder called ‘Products’. This file must contain at least 3 canned products of your choice.

mkdir "Designed_task"/{"Products"}
touch "Designed_task"/"Products"/cosa1
touch "Designed_task"/"Products"/cosa2
touch "Designed_task"/"Products"/cosa3

#e. Modify the ‘dates’ files adding: ‘Maintenance - Friday, ‘Production line – Monday to Thursday’, ‘Fixes
echo "Maintenance - Friday" > "Designed_task"/"Maintenance"/dates
echo "Production line – Monday to Thursday" > "Designed tasks"/"Production Line"/dates
echo "Fixes – with 2 days of anticipation" > "Designed tasks"/"Fixes"/dates
echo "Costs – at the end of the month" > "Designed tasks"/"Costs"/dates



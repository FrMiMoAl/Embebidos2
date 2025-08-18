#A canning company wants to use Ubuntu as their main OS for their activities. You have been hired to develop the following features:
#a. Create a user called ‘Company’ with super user privileges.
#b. Create a user called ‘Engineer’.
#c. Create a user called ‘Operator’.
#d. All these users must belong to the ‘Distribution’ group

sudo add user company
sudo usermod -aG sudo company

sudo add user engineer
sudo usermod -aG sudo engineer

sudo add user operator
sudo usermod -aG sudo operator


sudo grupoadd Distribution

sudo usermod -aG Distribution company
sudo usermod -aG Distribution engineer
sudo usermod -aG Distribution operator

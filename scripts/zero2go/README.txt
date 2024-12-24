The zero2go seems to change its slave address.  To set it back to 0x29

sudo i2cdetect -y 1

This will give you the current address

Using the current address execute the following using the current address
i2cset -y 1 0x1d 9 0x29

You must power cycle not reboot
#!/bin/bash
# NaviPi update script by KreAch3R

function deps_update {
    echo "Installing required software."
    # Include here all the necessary dependencies
    sudo apt-get install libgeos-dev
    pip3 install geocoder
    pip3 install gps
    pip3 install astral
    pip3 install tzwhere
}

function services_update {
    echo "Enabling services"
    # Include here all the necessary changes to services
    sudo systemctl enable daynightlocation.timer
}

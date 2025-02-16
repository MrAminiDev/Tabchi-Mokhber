#!/bin/bash

install_tabchi_mokhber() {
    echo "Starting installation process..."

    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip -y
    pip install uv
    sudo apt install wget unzip -y
    mkdir -p mokhber
    wget -O tabchi-mokhber.zip https://github.com/MrAminiDev/Tabchi-Mokhber/archive/refs/heads/main.zip
    unzip tabchi-mokhber.zip -d mokhber
    mv mokhber/Tabchi-Mokhber-main/* mokhber/
    rm -r mokhber/Tabchi-Mokhber-main
    rm tabchi-mokhber.zip

    read -p "Enter your API_ID: " api_id
    sed -i "s/AminiMokhberAPIID/$api_id/" mokhber/main.py

    read -p "Enter your API_HASH: " api_hash
    sed -i "s/AminiMokhberAPIHASH/$api_hash/" mokhber/main.py

    read -p "Enter your Admin ID: " admin_id
    sed -i "s/AminiMokhberADMINID/$admin_id/" mokhber/main.py

    uv run mokhber/main.py

    echo "Your bot has been successfully run. Check the commands using the 'Help' command in Telegram."
}

update_tabchi_mokhber() {
    echo "Updating Tabchi Mokhber..."
    install_tabchi_mokhber
}

uninstall_tabchi_mokhber() {
    echo "Removing mokhber folder..."
    sudo rm -rf mokhber
}

create_service() {
    echo "Creating systemd service..."
    sudo bash -c 'cat > /etc/systemd/system/mokhber.service <<EOF
[Unit]
Description=mokhber
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mokhber
ExecStart=/usr/local/bin/uv run main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

    sudo systemctl daemon-reload
    sudo systemctl enable mokhber.service
    sudo systemctl start mokhber.service
}

# منوی اصلی
while true; do
    clear
    echo "1. Install Tabchi Mokhber"
    echo "2. Update"
    echo "3. Uninstall"
    echo "0. Exit"
    read -p "Choose an option: " option

    case $option in
        1)
            install_tabchi_mokhber
            create_service
            ;;
        2)
            update_tabchi_mokhber
            ;;
        3)
            uninstall_tabchi_mokhber
            ;;
        0)
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    read -p "Press [Enter] to continue..."
done

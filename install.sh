
# This is an auto install script for Oracle Autonomous Linux 7.9
# It will configure to automatically run the script using Instance Principals permission
# So ensure you have configured a dynamic group for this instance and that that dynamic group
# has a policy including proper statements.

# Install needed components and configure crontab
sudo yum update -y
sudo yum install git -y
python3 -m pip install oci oci-cli --user

git clone https://github.com/Olygo/OCI-TagCompute.git

cd OCI-TagCompute/
crontab schedule.cron
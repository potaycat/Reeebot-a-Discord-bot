
```
apt update && apt -y install git docker.io
git clone https://github.com/potaycat/reeebot-deploy.git
cd reeebot-deploy/runpod-api/sd-kemono
echo @9GXXcBFKz6Tc6d | docker login --username longnhfvtap --password-stdin
git fetch && git pull && docker build -t longnhfvtap/kemono-sd:1.2 .
docker push longnhfvtap/kemono-sd:1.2
```

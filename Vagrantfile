# -*- mode: ruby -*-
# vi: set ft=ruby -*-

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.hostname = "sre-pipeline"
  config.vm.network "private_network", ip: "10.0.0.10"

  config.vm.provider "virtualbox" do |vb|
    vb.cpus = 2
    vb.memory = "2048"
  end
  
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update -qq
    apt-get upgrade -y -qq
    apt-get install -y -qq build-essential
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker vagrant
    docker compose -f /vagrant/compose.yaml up -d
  SHELL
end

# platform-appstack

Cloud Foundry platform definition files to be used with https://github.com/trustedanalytics/cloudfoundry-mkappstack.

Edit template_variables.yml file.
You should obtain missing values from the sources listed below.

1) EC2 instance where platform will be deployed

From:
```
~/workspace/deployments/docker-services-boshworkspace/deployments/docker-aws-vpc.yml
```
obtain:  
* nats_ip (meta/nats/machines)  

From:
```
~/workspace/deployments/cf-boshworkspace/deployments/cf-aws-tiny.yml
```
obtain:  
* cf_admin_password (meta/admin_secret)  
* cf_admin_client_password (meta/secret)  
* apps_domain (meta/app_domains)  
* developer_console_password (meta/secret)  
* email_address (meta/login_smtp/senderEmail)  
* run_domain (meta/domain)  
* smtp_pass (meta/login_smtp/password)  
* smtp_user (meta/login_smtp/user)  

2) From Cloudera Manager UI, obtain:
* gearpump_webui_server_host (Status/Gearpump/WebUI Server/Host)
* master_node_ip_1 (Zookeeper/Instances)
* master_node_ip_2 (Zookeeper/Instances)
* master_node_ip_3 (Zookeeper/Instances)
* namenode_internal_host (HDFS, Namenode summary)
* cloudera_manager_internal_host (Hosts, search for Cloudera)
* kerberos_host - the same as cloudera_manager_internal_host

3) Other sources:
* import_hadoop_conf (follow instructions in [Hadoop Admin Tools](https://github.com/trustedanalytics/hadoop-admin-tools) repository).

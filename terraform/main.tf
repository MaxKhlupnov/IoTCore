provider "yandex" {
  version   = "~> 0.29"
  token     = var.yc_oauth_token
  cloud_id  = var.yc_cloud_id
  folder_id = var.yc_folder_id
  zone      = var.yc_main_zone
}


resource "yandex_iam_service_account" "sa" {
  name        = "svc-iot-mngr"
  description = "service account to work with IoT functoions"
}

resource "yandex_iam_service_account_iam_member" "admin-account-iam" {
  service_account_id = "${yandex_iam_service_account.sa.id}"
  role               = "serverless.functions.invoker"
  member             = "serviceAccount:${yandex_iam_service_account.sa.id}"
}

resource "random_password" "password" {
  length = 16
  special = true
  min_special = 1
  upper = true
  min_upper = 1
  lower = true
  min_lower = 1
  number = true
  min_numeric = 1
  override_special = "_%@"
}

resource "yandex_iot_core_registry" "iot_registry_name" {
  name        = "iot_registry_name"
  description = "yandex iot example registry"
  labels = {
    my-label = "yandex-iot-example"
  }
  passwords = [
    random_password.password.result
  ]
}

resource "yandex_iot_core_device" "iot_device_01_name" {
  registry_id = "${yandex_iot_core_registry.iot_registry_name.id}"
  name        = "iot_device_01_name"
  description = "yandex iot example device"
   passwords = [
    random_password.password.result
  ]
}
data "archive_file" "function_packer" {
  output_path = "${path.module}/iotadapter.zip"
  source_file = "../iotadapter.py"
  type        = "zip"
}

module "iot-vpc" {
  source       = "./modules/vpc"
  network_name = "iot-network"
  subnets = {
    "iot-data-subnet" : {
      zone           = var.yc_main_zone
      v4_cidr_blocks = ["10.0.1.0/24"]
    }
  }
}


module "managed_pgsql_iot_testing" {

  source       = "./modules/mdb-postgresql"
  cluster_name = "iot_testing"
  network_id   =  module.iot-vpc.vpc_network_id
  description  = "IoT testing PostgreSQL database"
  labels = {
    env        = "iot",
    deployment = "terraform"
  }
  environment        = "PRESTABLE"
  resource_preset_id = "b2.medium"
  disk_size          = 50

  hosts = [
    {
      zone             = var.yc_main_zone
      subnet_id        = module.iot-vpc.subnet_ids_by_names["iot-data-subnet"]
      assign_public_ip = true
    }
  ]
  users = [
    {
      name     = "iot_db_user"
      password = random_password.password.result
    }
  ]
  databases = [
    {
      name  = var.iot_db_name
      owner = "iot_db_user"
    }
  ]
  user_permissions = {
    "iot_db_user" : [
      {
        database_name = var.iot_db_name
      }
    ]}

}

resource "yandex_function" "iotadapter" {
  name               = "iotadapter"
  description        = "serverless function take incomming events from IoT Core and store this events in PostgreSql Db"
  user_hash          = "any_user_defined_string"
  runtime            = "python37"
  entrypoint         = "iotadapter.msgHandler"
  memory             = "128"
  execution_timeout  = "10"
  service_account_id =  "${yandex_iam_service_account.sa.id}"
  tags               = ["yandex-iot-example"]
  content {
    zip_filename = "iotadapter.zip"
  }
  environment        = {
    DB_HOSTNAME  = "${module.managed_pgsql_iot_testing.cluster_hosts_fqdns[0][0]}"
    DB_PORT      = 6432
    DB_USER      = "iot_db_user"
    DB_PASSWORD  = "${module.managed_pgsql_iot_testing.cluster_users_passwords["iot_db_user"]}"
    DB_NAME      = var.iot_db_name
    VERBOSE_LOG  = "True"
  }
}

resource "yandex_function_trigger" "iot_device_01" {
  name        = "dev-${yandex_iot_core_device.iot_device_01_name.id}-trigger"
  description = "trigger for incomming iot messages for iot_device_01"
  iot  {
      registry_id = "${yandex_iot_core_registry.iot_registry_name.id}"
      device_id = "${yandex_iot_core_device.iot_device_01_name.id}"
      topic = "$devices/${yandex_iot_core_device.iot_device_01_name.id}/events"
  }
  function  {
    id = "${yandex_function.iotadapter.id}"
    service_account_id = "${yandex_iam_service_account.sa.id}"
  }
}

output "yandex_iot_core_registry_iot_registry_passwords" {
  value = "${yandex_iot_core_registry.iot_registry_name.passwords}"
}

output "yandex_iot_core_device_iot_device_01_passwords" {
  value = "${yandex_iot_core_device.iot_device_01_name.passwords}"
}

output "managed_pgsql_iot_testing_cluster_id" {
  value = module.managed_pgsql_iot_testing.cluster_id
}

output "managed_pgsql_iot_testing_cluster_fqdns" {
  value = module.managed_pgsql_iot_testing.cluster_hosts_fqdns
}

output "managed_pgsql_iot_testing_cluster_users" {
  value = module.managed_pgsql_iot_testing.cluster_users
}

output "managed_pgsql_iot_testing_cluster_users_passwords" {
  value     = module.managed_pgsql_iot_testing.cluster_users_passwords
  sensitive = true
}

output "managed_pgsql_iot_testing_cluster_fips" {
  value = module.managed_pgsql_iot_testing.cluster_hosts_fips
}

output "managed_pgsql_iot_testing_cluster_databases" {
  value = module.managed_pgsql_iot_testing.cluster_databases
}


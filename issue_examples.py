DEFAULT_ISSUE_BODY = """

Title: Support for AKS API Server VNet Integration

## Is there an existing issue for this?

I have searched the existing issues

## Description

AKS API Server VNet Integration. The product is still in preview but let's track it in a GitHub issue so we are ready to merge a PR as soon is promoted to GA.

Status:

- Product still in preview.
- Implementation in the Terraform provider is available. https://registry.terraform.io/providers/hashicorp/azurerm/3.61.0/docs/resources/kubernetes_cluster#vnet_integration_enabled

## New or Affected Resource(s)/Data Source(s)

azurerm_kubernetes_cluster

## Potential Terraform Configuration

```hcl
variable "vnet_integration_enabled" {
  type        = bool
  default     = false
  description = "(Optional) Should API Server VNet Integration be enabled? For more details please visit Use API Server VNet Integration."
}

resource "azurerm_kubernetes_cluster" "main" {
   [..CUT..]
   vnet_integration_enabled = var.vnet_integration_enabled
   [..CUT..]

}
```

## References

No response

"""

DEFAULT_BUG_BODY = """

Title: Cannot create a new AKS cluster with additional node pools using the resource azurerm_kubernetes_cluster_node_pool directly

### Is there an existing issue for this?

- [X] I have searched the existing issues

### Greenfield/Brownfield provisioning

greenfield

### Terraform Version

Terraform v1.5.4

### Module Version

7.2.0

### AzureRM Provider Version

v3.67.0

### Affected Resource(s)/Data Source(s)

azure_kubernetes_cluster

### Terraform Configuration Files

```hcl
resource "random_string" "random" {
  length  = 6
  special = false
  upper   = false
}

module "aks-westeurope" {
  source                            = "Azure/aks/azurerm"
  version                           = "7.2.0"
  resource_group_name               = azurerm_resource_group.westeurope.name
  kubernetes_version                = var.kubernetes_version
  orchestrator_version              = var.kubernetes_version
  prefix                            = azurerm_resource_group.westeurope.location
  network_plugin                    = "azure"
  vnet_subnet_id                    = module.network-westeurope.vnet_subnets[0]
  os_disk_size_gb                   = 50
  sku_tier                          = "Standard"
  role_based_access_control_enabled = true
  rbac_aad_admin_group_object_ids   = var.rbac_aad_admin_group_object_ids
  rbac_aad_managed                  = true
  private_cluster_enabled           = false
  http_application_routing_enabled  = false
  azure_policy_enabled              = true
  enable_auto_scaling               = true
  enable_host_encryption            = false
  log_analytics_workspace_enabled   = false
  agents_min_count                  = 1
  agents_max_count                  = 5
  agents_count                      = null # Please set `agents_count` `null` while `enable_auto_scaling` is `true` to avoid possible `agents_count` changes.
  agents_max_pods                   = 100
  agents_pool_name                  = "system"
  agents_availability_zones         = ["1", "2"]
  agents_type                       = "VirtualMachineScaleSets"
  agents_size                       = var.agents_size

  agents_labels = {
    "nodepool" : "defaultnodepool"
  }

  agents_tags = {
    "Agent" : "defaultnodepoolagent"
  }

  ingress_application_gateway_enabled   = true
  ingress_application_gateway_name      = "aks-agw-westeurope"
  ingress_application_gateway_subnet_id = module.network-westeurope.vnet_subnets[2]

  network_policy                 = "azure"
  net_profile_dns_service_ip     = "10.0.0.10"
  net_profile_service_cidr       = "10.0.0.0/16"

  key_vault_secrets_provider_enabled = true
  secret_rotation_enabled            = true
  secret_rotation_interval           = "3m"

  depends_on = [module.network-westeurope]
}
module "network-westeurope" {
  source              = "Azure/network/azurerm"
  vnet_name           = azurerm_resource_group.westeurope.name
  resource_group_name = azurerm_resource_group.westeurope.name
  address_space       = "10.53.0.0/16"
  subnet_prefixes     = ["10.53.0.0/24", "10.53.1.0/24", "10.53.200.0/24"]
  subnet_names        = ["system", "user", "appgw"]
  depends_on          = [azurerm_resource_group.westeurope]
  subnet_enforce_private_link_endpoint_network_policies = {
    "subnet1" : true
  }
  use_for_each        = true
}
resource "azurerm_kubernetes_cluster_node_pool" "westuserpool" {
  name                  = "user"
  kubernetes_cluster_id = module.aks-westeurope.aks_id
  vm_size               = var.agents_size
  enable_auto_scaling   = true
  node_count            = 1
  min_count             = 1
  max_count             = 5
  vnet_subnet_id        = module.network-westeurope.vnet_subnets[1]
  depends_on            = [module.network-westeurope]
}
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.10"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

resource "azurerm_resource_group" "westeurope" {
  name     = "bug"
  location = "westeurope"
}
variable "agents_size" {
  default     = "Standard_D2s_v3"
  description = "The default virtual machine size for the Kubernetes agents"
  type        = string
}

variable "rbac_aad_admin_group_object_ids" {
  description = "Object ID of Active Directory groups with admin access."
  type        = list(string)
  default     = null
}

variable "kubernetes_version" {
  description = "Specify which Kubernetes release to use. The default used is the latest Kubernetes version available in the region"
  type        = string
  default     = null
}
```


### tfvars variables values

```hcl
Using default values
```


### Debug Output/Panic Output

```shell
Error: creating/updating "Resource: (ResourceId \"/subscriptions/9b70acd9-975f-44ba-bad6-255a2c8bda37/resourceGroups/bug/providers/Microsoft.ContainerService/managedClusters/westeurope-aks\" / Api Version \"2023-01-02-preview\")": PUT https://management.azure.com/subscriptions/9b70acd9-975f-44ba-bad6-255a2c8bda37/resourceGroups/bug/providers/Microsoft.ContainerService/managedClusters/westeurope-aks
│ --------------------------------------------------------------------------------
│ RESPONSE 409: 409 Conflict
│ ERROR CODE: OperationNotAllowed
│ --------------------------------------------------------------------------------
│ {
│   "code": "OperationNotAllowed",
│   "details": null,
│   "message": "Operation is not allowed: Another agentpool operation (user - Creating) is in progress, please wait for it to finish before starting a new operation. See https://aka.ms/aks-pending-operation for more details",
│   "subcode": ""
│ }
│ --------------------------------------------------------------------------------
│
│
│   with module.aks-westeurope.azapi_update_resource.aks_cluster_post_create,
│   on .terraform/modules/aks-westeurope/main.tf line 508, in resource "azapi_update_resource" "aks_cluster_post_create":
│  508: resource "azapi_update_resource" "aks_cluster_post_create" {
```


### Expected Behaviour

Terraform should have completed without errors

### Actual Behaviour

_No response_

### Steps to Reproduce

_No response_

### Important Factoids

_No response_

### References

_No response_
"""
DEFAULT_ISSUE_BODY = """

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
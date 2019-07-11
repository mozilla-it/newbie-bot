# SRE Info
This is the SRE_INFO.md file which should be found in the root of any source code that is
administered by the Mozilla IT SRE team. We are available on #it-sre on slack.

## Infra Access
Currently this is a Kops built cluster and requires the ~/.kube/config file to be present
so that k8s commands will work.  This is usually acquired via gpg, passed from someone on the #it-sre team.

[SRE aws-vault setup](https://mana.mozilla.org/wiki/display/SRE/aws-vault)

[SRE account guide](https://mana.mozilla.org/wiki/display/SRE/AWS+Account+access+guide)

[SRE AWS accounts](https://github.com/mozilla-it/itsre-accounts/blob/master/accounts/mozilla-itsre/terraform.tfvars#L5)

## Secrets
Secrets are handled by k8s builtin secrets handling

## Source Repos
[newbie-bot](https://github.com/mozilla-it/newbie-bot)

## Monitoring

### SSL Expiry checks in New Relic
[newbie.mozilla-slack.app](https://synthetics.newrelic.com/accounts/2239138/monitors/554cb212-7ab3-494d-af42-73495bf01ac7)
## SSL Certificates
newbie uses LE certificates via the Voyager Ingress Controller

## Cloud Account
AWS account connected-workplace 932424332618

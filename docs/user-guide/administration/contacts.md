---
description: Configuring Dispatch's contact repository
---

# Contacts

## Individual

In Dispatch, Individuals are either internal or external people identifiers. Typically, an organization will have a robust internal whitepages/phone-book. Dispatch does not expect to replace those data stores, instead it keeps a lightweight notion of identities to associate with incidents.

Everyone has a spreadsheet somewhere of who to contact for a given incident. Dispatch allows the folks to be pulled directly into an incident. By assigning individuals terms, incident types or incident priorities dispatch is able to directly add those the folks \(if internal\) or suggest reaching out \(if external\).  

## Team

Like `Individuals`, there are often groups of individuals that need to be engaged and/or notified during an incident. Here we give you a place to manage those team \(typically, team distribution lists\), and have Dispatch help keep those folks up-to-date. 

## Service

Similar to `Teams` there are often groups of individuals responsible for a an application or service which need to be involved in an incident. However, in these circumstances you don't want to engage the _whole_ team. Here we only want to engage the on-call person. Services are the way to resolve things like PagerDuty schedules \(built-in\). 


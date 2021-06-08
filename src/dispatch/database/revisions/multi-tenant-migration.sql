CREATE OR REPLACE FUNCTION clone_schema(source_schema text, dest_schema text) RETURNS void AS
$BODY$
DECLARE
  objeto text;
  buffer text;
BEGIN
    EXECUTE 'CREATE SCHEMA ' || dest_schema ;

    FOR objeto IN
        SELECT table_name::text FROM information_schema.tables WHERE table_schema = source_schema
    LOOP
        buffer := dest_schema || '.' || objeto;
        EXECUTE 'CREATE TABLE ' || buffer || ' (LIKE ' || source_schema || '.' || objeto || ' INCLUDING CONSTRAINTS INCLUDING INDEXES INCLUDING DEFAULTS)';
        EXECUTE 'INSERT INTO ' || buffer || '(SELECT * FROM ' || source_schema || '.' || objeto || ')';
    END LOOP;

END;
$BODY$
LANGUAGE plpgsql VOLATILE;

select clone_schema('public', 'dispatch_core');
select clone_schema('public', 'dispatch_organization_default');

-- drop tables that aren't needed
drop table dispatch_organization_default.dispatch_user;
drop table dispatch_organization_default.organization;
drop table dispatch_organization_default.dispatch_user_organization;

drop table dispatch_core.assoc_document_filters;
drop table dispatch_core.assoc_incident_tags;
drop table dispatch_core.assoc_incident_terms;
drop table dispatch_core.assoc_individual_contact_filters;
drop table dispatch_core.assoc_individual_contact_incident_priority;
drop table dispatch_core.assoc_individual_contact_incident_type;
drop table dispatch_core.assoc_individual_contact_terms;
drop table dispatch_core.assoc_notification_filters;
drop table dispatch_core.assoc_service_filters;
drop table dispatch_core.assoc_team_contact_filters;
drop table dispatch_core.conference;
drop table dispatch_core.conversation;
drop table dispatch_core.definition;
drop table dispatch_core.definition_teams;
drop table dispatch_core.definition_terms;
drop table dispatch_core.dispatch_user_project;
drop table dispatch_core.document;
drop table dispatch_core.document_incident_priority;
drop table dispatch_core.document_incident_type;
drop table dispatch_core.document_terms;
drop table dispatch_core.event;
drop table dispatch_core.feedback;
drop table dispatch_core.group;
drop table dispatch_core.incident;
drop table dispatch_core.incident_cost;
drop table dispatch_core.incident_cost_type;
drop table dispatch_core.incident_priority;
drop table dispatch_core.incident_type;
drop table dispatch_core.individual_contact;
drop table dispatch_core.notification;
drop table dispatch_core.participant;
drop table dispatch_core.participant_role;
drop table dispatch_core.plugin;
drop table dispatch_core.plugin_instance;
drop table dispatch_core.project;
drop table dispatch_core.recommendation;
drop table dispatch_core.recommendation_accuracy;
drop table dispatch_core.recommendation_documents;
drop table dispatch_core.recommendation_incident_priorities;
drop table dispatch_core.recommendation_incident_types;
drop table dispatch_core.recommendation_individual_contacts;
drop table dispatch_core.recommendation_match;
drop table dispatch_core.recommendation_services;
drop table dispatch_core.recommendation_team_contacts;
drop table dispatch_core.recommendation_terms;
drop table dispatch_core.report;
drop table dispatch_core.search_filter;
drop table dispatch_core.service;
drop table dispatch_core.service_incident;
drop table dispatch_core.service_incident_priority;
drop table dispatch_core.service_incident_type;
drop table dispatch_core.service_terms;
drop table dispatch_core.storage;
drop table dispatch_core.tag;
drop table dispatch_core.tag_type;
drop table dispatch_core.task;
drop table dispatch_core.task_assignees;
drop table dispatch_core.task_tickets;
drop table dispatch_core.team_contact;
drop table dispatch_core.team_contact_incident;
drop table dispatch_core.team_contact_incident_priority;
drop table dispatch_core.team_contact_incident_type;
drop table dispatch_core.team_contact_terms;
drop table dispatch_core.term;
drop table dispatch_core.ticket;
drop table dispatch_core.workflow;
drop table dispatch_core.workflow_incident_priority;
drop table dispatch_core.workflow_incident_type;
drop table dispatch_core.workflow_instance;
drop table dispatch_core.workflow_instance_artifact;
drop table dispatch_core.workflow_term;

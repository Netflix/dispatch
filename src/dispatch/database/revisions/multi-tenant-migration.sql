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

select clone_schema('public', 'dispatch');
select clone_schema('public', 'dispatch_organization_default');

-- drop tables that aren't needed
drop table dispatch_organization_default.dispatch_user;
drop table dispatch_organization_default.organization;
drop table dispatch_organization_default.dispatch_user_organization;

drop table dispatch.assoc_document_filters;
drop table dispatch.assoc_incident_tags;
drop table dispatch.assoc_incident_terms;
drop table dispatch.assoc_individual_contact_filters;
drop table dispatch.assoc_individual_contact_incident_priority;
drop table dispatch.assoc_individual_contact_incident_type;
drop table dispatch.assoc_individual_contact_terms;
drop table dispatch.assoc_notification_filters;
drop table dispatch.assoc_service_filters;
drop table dispatch.assoc_team_contact_filters;
drop table dispatch.conference;
drop table dispatch.conversation;
drop table dispatch.definition;
drop table dispatch.definition_teams;
drop table dispatch.definition_terms;
drop table dispatch.dispatch_user_project;
drop table dispatch.document;
drop table dispatch.document_incident_priority;
drop table dispatch.document_incident_type;
drop table dispatch.document_terms;
drop table dispatch.event;
drop table dispatch.feedback;
drop table dispatch.group;
drop table dispatch.incident;
drop table dispatch.incident_cost;
drop table dispatch.incident_cost_type;
drop table dispatch.incident_priority;
drop table dispatch.incident_type;
drop table dispatch.individual_contact;
drop table dispatch.notification;
drop table dispatch.participant;
drop table dispatch.participant_role;
drop table dispatch.plugin;
drop table dispatch.plugin_instance;
drop table dispatch.project;
drop table dispatch.recommendation;
drop table dispatch.recommendation_accuracy;
drop table dispatch.recommendation_documents;
drop table dispatch.recommendation_incident_priorities;
drop table dispatch.recommendation_incident_types;
drop table dispatch.recommendation_individual_contacts;
drop table dispatch.recommendation_match;
drop table dispatch.recommendation_services;
drop table dispatch.recommendation_team_contacts;
drop table dispatch.recommendation_terms;
drop table dispatch.report;
drop table dispatch.search_filter;
drop table dispatch.service;
drop table dispatch.service_incident;
drop table dispatch.service_incident_priority;
drop table dispatch.service_incident_type;
drop table dispatch.service_terms;
drop table dispatch.storage;
drop table dispatch.tag;
drop table dispatch.tag_type;
drop table dispatch.task;
drop table dispatch.task_assignees;
drop table dispatch.task_tickets;
drop table dispatch.team_contact;
drop table dispatch.team_contact_incident;
drop table dispatch.team_contact_incident_priority;
drop table dispatch.team_contact_incident_type;
drop table dispatch.team_contact_terms;
drop table dispatch.term;
drop table dispatch.ticket;
drop table dispatch.workflow;
drop table dispatch.workflow_incident_priority;
drop table dispatch.workflow_incident_type;
drop table dispatch.workflow_instance;
drop table dispatch.workflow_instance_artifact;
drop table dispatch.workflow_term;

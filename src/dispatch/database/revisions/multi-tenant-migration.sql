CREATE OR REPLACE FUNCTION clone_schema(source_schema text, dest_schema text) RETURNS void AS
$$

DECLARE
  object text;
  buffer text;
  default_ text;
  column_ text;
  constraint_name_ text;
  constraint_def_ text;
  trigger_name_ text;
  trigger_timing_ text;
  trigger_events_ text;
  trigger_orientation_ text;
  trigger_action_ text;
BEGIN

  -- replace existing schema
  EXECUTE 'DROP SCHEMA IF EXISTS ' || dest_schema || ' CASCADE';

  -- create schema
  EXECUTE 'CREATE SCHEMA ' || dest_schema ;

  -- create sequences
  FOR object IN
    SELECT sequence_name::text FROM information_schema.SEQUENCES WHERE sequence_schema = source_schema
  LOOP
    EXECUTE 'CREATE SEQUENCE ' || dest_schema || '.' || object;
  END LOOP;

  -- create tables
  FOR object IN
    SELECT table_name::text FROM information_schema.TABLES WHERE table_schema = source_schema
  LOOP
    buffer := dest_schema || '.' || object;

    -- create table
    EXECUTE 'CREATE TABLE ' || buffer || ' (LIKE ' || source_schema || '.' || object || ' INCLUDING CONSTRAINTS INCLUDING INDEXES INCLUDING DEFAULTS)';
    EXECUTE 'INSERT INTO ' || buffer || '(SELECT * FROM ' || source_schema || '.' || object || ')';

    -- fix sequence defaults
    FOR column_, default_ IN
      SELECT column_name::text, REPLACE(column_default::text, source_schema || '.', dest_schema|| '.') FROM information_schema.COLUMNS WHERE table_schema = dest_schema AND table_name = object AND column_default LIKE 'nextval(%' || source_schema || '.%::regclass)'
    LOOP
      EXECUTE 'ALTER TABLE ' || buffer || ' ALTER COLUMN ' || column_ || ' SET DEFAULT ' || default_;
    END LOOP;

    -- create triggers
    FOR trigger_name_, trigger_timing_, trigger_events_, trigger_orientation_, trigger_action_ IN
      SELECT trigger_name::text, action_timing::text, string_agg(event_manipulation::text, ' OR '), action_orientation::text, action_statement::text FROM information_schema.TRIGGERS WHERE event_object_schema=source_schema and event_object_table=object GROUP BY trigger_name, action_timing, action_orientation, action_statement
    LOOP
      EXECUTE 'CREATE TRIGGER ' || trigger_name_ || ' ' || trigger_timing_ || ' ' || trigger_events_ || ' ON ' || buffer || ' FOR EACH ' || trigger_orientation_ || ' ' || trigger_action_;
    END LOOP;
  END LOOP;

  -- reiterate tables and create foreign keys
  FOR object IN
    SELECT table_name::text FROM information_schema.TABLES WHERE table_schema = source_schema
  LOOP
    buffer := dest_schema || '.' || object;

    -- create foreign keys
    FOR constraint_name_, constraint_def_ IN
      SELECT conname::text, REPLACE(pg_get_constraintdef(pg_constraint.oid), source_schema||'.', dest_schema||'.') FROM pg_constraint INNER JOIN pg_class ON conrelid=pg_class.oid INNER JOIN pg_namespace ON pg_namespace.oid=pg_class.relnamespace WHERE contype='f' and relname=object and nspname=source_schema
    LOOP
      EXECUTE 'ALTER TABLE '|| buffer ||' ADD CONSTRAINT '|| constraint_name_ ||' '|| constraint_def_;
    END LOOP;
  END LOOP;

END;

$$ LANGUAGE plpgsql VOLATILE;


select clone_schema('public', 'dispatch_core');
select clone_schema('public', 'dispatch_organization_default');

-- drop table that aren't needed
drop table IF EXISTS dispatch_organization_default.dispatch_user;
drop table IF EXISTS dispatch_organization_default.organization;
drop table IF EXISTS dispatch_organization_default.dispatch_user_organization;
drop table IF EXISTS dispatch_organization_default.plugin;
drop table IF EXISTS dispatch_core.assoc_document_filters;
drop table IF EXISTS dispatch_core.assoc_incident_tags;
drop table IF EXISTS dispatch_core.assoc_incident_terms;
drop table IF EXISTS dispatch_core.assoc_individual_contact_filters;
drop table IF EXISTS dispatch_core.assoc_individual_contact_incident_priority;
drop table IF EXISTS dispatch_core.assoc_individual_contact_incident_type;
drop table IF EXISTS dispatch_core.assoc_individual_contact_terms;
drop table IF EXISTS dispatch_core.assoc_notification_filters;
drop table IF EXISTS dispatch_core.assoc_service_filters;
drop table IF EXISTS dispatch_core.assoc_team_contact_filters;
drop table IF EXISTS dispatch_core.conference;
drop table IF EXISTS dispatch_core.conversation;
drop table IF EXISTS dispatch_core.definition;
drop table IF EXISTS dispatch_core.definition_teams;
drop table IF EXISTS dispatch_core.definition_terms;
drop table IF EXISTS dispatch_core.dispatch_user_project;
drop table IF EXISTS dispatch_core.document;
drop table IF EXISTS dispatch_core.document_incident_priority;
drop table IF EXISTS dispatch_core.document_incident_type;
drop table IF EXISTS dispatch_core.document_terms;
drop table IF EXISTS dispatch_core.event;
drop table IF EXISTS dispatch_core.feedback;
drop table IF EXISTS dispatch_core.group;
drop table IF EXISTS dispatch_core.incident;
drop table IF EXISTS dispatch_core.incident_cost;
drop table IF EXISTS dispatch_core.incident_cost_type;
drop table IF EXISTS dispatch_core.incident_priority;
drop table IF EXISTS dispatch_core.incident_type;
drop table IF EXISTS dispatch_core.individual_contact;
drop table IF EXISTS dispatch_core.notification;
drop table IF EXISTS dispatch_core.participant;
drop table IF EXISTS dispatch_core.participant_role;
drop table IF EXISTS dispatch_core.plugin_instance;
drop table IF EXISTS dispatch_core.project;
drop table IF EXISTS dispatch_core.recommendation;
drop table IF EXISTS dispatch_core.recommendation_accuracy;
drop table IF EXISTS dispatch_core.recommendation_documents;
drop table IF EXISTS dispatch_core.recommendation_incident_priorities;
drop table IF EXISTS dispatch_core.recommendation_incident_types;
drop table IF EXISTS dispatch_core.recommendation_individual_contacts;
drop table IF EXISTS dispatch_core.recommendation_match;
drop table IF EXISTS dispatch_core.recommendation_services;
drop table IF EXISTS dispatch_core.recommendation_team_contacts;
drop table IF EXISTS dispatch_core.recommendation_terms;
drop table IF EXISTS dispatch_core.report;
drop table IF EXISTS dispatch_core.search_filter;
drop table IF EXISTS dispatch_core.service;
drop table IF EXISTS dispatch_core.service_incident;
drop table IF EXISTS dispatch_core.service_incident_priority;
drop table IF EXISTS dispatch_core.service_incident_type;
drop table IF EXISTS dispatch_core.service_terms;
drop table IF EXISTS dispatch_core.storage;
drop table IF EXISTS dispatch_core.tag;
drop table IF EXISTS dispatch_core.tag_type;
drop table IF EXISTS dispatch_core.task;
drop table IF EXISTS dispatch_core.task_assignees;
drop table IF EXISTS dispatch_core.task_tickets;
drop table IF EXISTS dispatch_core.team_contact;
drop table IF EXISTS dispatch_core.team_contact_incident;
drop table IF EXISTS dispatch_core.team_contact_incident_priority;
drop table IF EXISTS dispatch_core.team_contact_incident_type;
drop table IF EXISTS dispatch_core.team_contact_terms;
drop table IF EXISTS dispatch_core.term;
drop table IF EXISTS dispatch_core.ticket;
drop table IF EXISTS dispatch_core.workflow;
drop table IF EXISTS dispatch_core.workflow_incident_priority;
drop table IF EXISTS dispatch_core.workflow_incident_type;
drop table IF EXISTS dispatch_core.workflow_instance;
drop table IF EXISTS dispatch_core.workflow_instance_artifact;
drop table IF EXISTS dispatch_core.workflow_term;

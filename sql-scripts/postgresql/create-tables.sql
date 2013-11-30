
--
-- 'create-tables.sql'
-- 
-- Copyright (C) 2013 Jorge Couchet <jorge.couchet at gmail.com>
--
-- This file is part of 'ted-scimu'
-- 
-- 'ted-scimu' is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
-- 
-- 'ted-scimu' is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with 'ted-scimu'.  If not, see <http ://www.gnu.org/licenses/>.
--

------ *******************************************
------ *******************************************
------          start TED_TALKS
------ *******************************************
------ *******************************************

-- start table TED_TALKS

create sequence t_ted_talks_seq;

create view ted_talks_seq as
 select nextval('t_ted_talks_seq') as nextval;

-- The table is representing the ted talks
CREATE TABLE ted_talks (
        id             integer        CONSTRAINT ted_talks_id_pk
                                      PRIMARY KEY,
        -- The public talk id
        talk_id        integer        CONSTRAINT ted_talks_talk_id_un
                                      UNIQUE
                                      CONSTRAINT ted_talks_talk_id_nn
                                      NOT NULL,
        -- The talk public URL
        url            varchar        CONSTRAINT ted_talks_url_un
                                      UNIQUE
                                      CONSTRAINT ted_talks_url_nn
                                      NOT NULL,
        -- The talk speaker
        speaker        varchar        CONSTRAINT ted_talks_speaker_nn
                                      NOT NULL,
        -- The talk name
        name           varchar        CONSTRAINT ted_talks_name_nn
                                      NOT NULL,
        -- The talk event name
        event          varchar        CONSTRAINT ted_talks_event_nn
                                      NOT NULL,
        -- The talk summary
        summary        varchar        CONSTRAINT ted_talks_summary_nn
                                      NOT NULL,
        -- The talk duration
        duration       time,
        -- The talk publication date
        talk_date      date           CONSTRAINT ted_talks_talk_date_nn
                                      NOT NULL,
        subtitles      varchar        CONSTRAINT ted_talks_subtitles_nn
                                      NOT NULL
);


CREATE INDEX ted_talks_speaker_idx ON ted_talks USING btree(speaker);
CREATE INDEX ted_talks_event_idx ON ted_talks USING btree(event);
CREATE INDEX ted_talks_duration_idx ON ted_talks USING btree(duration);
CREATE INDEX ted_talks_talk_date_idx ON ted_talks USING btree(talk_date);
-- Using tsvector in order to have full text search over the summary and the subtitles
CREATE INDEX ted_talks_full_text_idx ON ted_talks USING gin(to_tsvector('english', coalesce(summary,'') || ' ' || coalesce(subtitles,'')));


-- end table TED_TALKS

------ *******************************************
------ *******************************************
------                end TED_TALKS
------ *******************************************
------ *******************************************


------ *******************************************
------ *******************************************
------          start SCIMU_OBJECTS
------ *******************************************
------ *******************************************

-- start table SCIMU_OBJECTS

create sequence t_scimu_objects_seq;

create view scimu_objects_seq as
 select nextval('t_scimu_objects_seq') as nextval;

-- The table is representing the objects from the Science Museum
CREATE TABLE scimu_objects (
        id             integer        CONSTRAINT scimu_objects_id_pk
                                      PRIMARY KEY,
        -- The public object id
        object_id      varchar        CONSTRAINT scimu_objects_object_id_un
                                      UNIQUE
                                      CONSTRAINT scimu_objects_object_id_nn
                                      NOT NULL,
        -- The object name
        name           varchar,
        -- The object title
        title          varchar,
        -- The object maker
        maker          varchar,
        -- The object 's date made
        date_made      varchar,
        -- The object 's place made
        place_made     varchar,
        -- The object description
        description    varchar
);


CREATE INDEX scimu_objects_maker_idx ON scimu_objects USING btree(maker);
CREATE INDEX scimu_objects_date_made_idx ON scimu_objects USING btree(date_made);
CREATE INDEX scimu_objects_place_made_idx ON scimu_objects USING btree(place_made);
-- Using tsvector in order to have full text search over the name, title and description
CREATE INDEX scimu_objects_full_text_idx ON scimu_objects USING gin(to_tsvector('english', coalesce(name,'') || ' ' || coalesce(title,'')  || ' ' || coalesce(description,'')));


-- end table SCIMU_OBJECTS

------ *******************************************
------ *******************************************
------              end SCIMU_OBJECTS
------ *******************************************
------ *******************************************


------ *******************************************
------ *******************************************
------          start SCIMU_MEDIA
------ *******************************************
------ *******************************************

-- start table SCIMU_MEDIA

create sequence t_scimu_media_seq;

create view scimu_media_seq as
 select nextval('t_scimu_media_seq') as nextval;

-- The table is representing the objects 's media from the Science Museum
CREATE TABLE scimu_media (
        id             integer        CONSTRAINT scimu_media_id_pk
                                      PRIMARY KEY,
        -- The object referenced by the media
        object_id      integer        CONSTRAINT scimu_media_object_id_fk
                                      REFERENCES scimu_objects(id) ON UPDATE NO ACTION ON DELETE CASCADE
                                      CONSTRAINT scimu_media_object_id_nn
                                      NOT NULL,
        -- The media public id
        media_id       varchar        CONSTRAINT scimu_media_media_id_un
                                      UNIQUE
                                      CONSTRAINT scimu_media_media_id_nn
                                      NOT NULL,
        -- The media public key
        media_key      varchar        CONSTRAINT scimu_media_media_key_un
                                      UNIQUE
                                      CONSTRAINT scimu_media_media_key_nn
                                      NOT NULL,
        -- The media caption
        caption        varchar
);


CREATE INDEX scimu_media_object_id_idx ON scimu_media USING btree(object_id);


-- end table SCIMU_MEDIA

------ *******************************************
------ *******************************************
------              end SCIMU_MEDIA
------ *******************************************
------ *******************************************


--
-- 'drop.sql'
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
------              start SCIMU_MEDIA
------ *******************************************
------ *******************************************


drop table scimu_media cascade;
drop view  scimu_media_seq cascade;
drop sequence t_scimu_media_seq cascade;


------ *******************************************
------ *******************************************
------              end SCIMU_MEDIA
------ *******************************************


------ *******************************************
------ *******************************************
------              start SCIMU_OBJECTS
------ *******************************************
------ *******************************************


drop table scimu_objects cascade;
drop view  scimu_objects_seq cascade;
drop sequence t_scimu_objects_seq cascade;


------ *******************************************
------ *******************************************
------              end SCIMU_OBJECTS
------ *******************************************



------ *******************************************
------ *******************************************
------              start TED_TALKS
------ *******************************************
------ *******************************************


drop table ted_talks cascade;
drop view  ted_talks_seq cascade;
drop sequence t_ted_talks_seq cascade;


------ *******************************************
------ *******************************************
------              end TED_TALKS
------ *******************************************

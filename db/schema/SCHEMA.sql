-- Property site schema

create schema dev;

-- tPostcode
-- Canonical list of postcodes
-- Index on postcode_1 and name (for place name lookup)
-- Desc is for info about place
create table dev.tpostcode (
	postcode_id serial,
	postcode_1  character varying(10)  not null,
	postcode_2  character varying(10),
	long        float4 not null, 
	lat         float4 not null,
	name        character varying(255),
	description text,
	constraint pk_tPostcode primary key(postcode_id)
);

create unique index idx_postcode_postcode on dev.tpostcode (postcode_1,postcode_2);

alter table dev.tpostcode
	alter long
	set default 0;

alter table dev.tpostcode
	alter lat
	set default 0;


-- tproperty
--
create table dev.tproperty (
	property_id serial,
	postcode_id integer not null,
	address_1 character varying (255) not null,
	address_2 character varying (255),
	address_3 character varying (255),
	county    character varying (100),
	country   character varying (30),
	constraint pk_tproperty primary key(property_id)
);

alter table dev.tproperty
	add constraint fk_property_postcode_id
	foreign key (postcode_id) references dev.tpostcode(postcode_id);


-- tpropertyvend
-- an individual vending/listing of a property on a site
-- duplicates can be id'd by property
-- num_beds - if null, means N/A
create table dev.tpropertyvend (
	property_vend_id serial,
	property_id      integer       not null,
	buy_type         character(1)  not null,
	property_source  character(3)  not null,
	cr_date          timestamp     not null,
	status           character(1)  not null,
	num_beds         integer,
	property_type    character(1)  not null,
	unique (property_id,buy_type,property_source),
	constraint pk_tpropertyvend primary key(property_vend_id)
);

alter table dev.tpropertyvend
	add constraint fk_propertyvend_property_id
	foreign key (property_id) references dev.tproperty(property_id);

alter table dev.tpropertyvend
	add constraint chk_propertyvend_1
	check (buy_type in ('R','B','A'));

-- 'F'or sale
-- 'U'nder offer
-- 'S'old
-- 'A'rchived
alter table dev.tpropertyvend
	add constraint chk_propertyvend_2
	check (status in ('F','U','S','A'));

alter table dev.tpropertyvend
	add constraint chk_propertyvend_3
	check (property_source in ('FAP','RM'));

-- "H"ouse
-- "F"lat
-- "C"ommercial
alter table dev.tpropertyvend
	add constraint chk_propertyvend_4
	check (property_type in ('H','F','C'));

alter table dev.tpropertyvend
	alter cr_date 
	set default current_date;


-- tpropertyhist
create table dev.tpropertyhist (
	property_price_hist_id serial,
	property_vend_id integer not null,
	update_date timestamp not null,
	price double not null,
	purchase_type character(2),
	status character(1),
	constraint pk_propertyhist primary key (property_price_hist_id)
);

-- 'N'ew
-- 'U'nder offer
-- 'R'educed
-- 'K'een to sell
-- 'S'old
alter table dev.tpropertythist
	add constraint chk_propertyhist_2
	check (fap_status in ('N','U','R','K','S'));


-- MR - monthly rental
-- WR - weekly rental
-- FP - freehold purchase
-- LP - leasehold purchase
-- CP - commercial purchase
-- CR - commercial rental
alter table dev.tpropertyhist
	add constraint chk_propertyhist_1
	check (purchase_type in ('MR','WR','FP','LP','CP','CR'));


-- tagent
-- All agents' information across sites will be stored in here
create table dev.tagent (
	agent_id serial,
	constraint pk_tagent primary key (agent_id)
);



-- Findaproperty property details
-- tpropertyfap
create table dev.tpropertyfap (
	property_vend_id   integer not null,
	agent_id           integer not null,
	fap_id             integer not null,
	constraint pk_tropertyfap primary key (fap_id)
);

alter table dev.tpropertyfap
	add constraint fk_propertyfap_source_id
	foreign key (property_vend_id) references dev.tpropertyvend(property_vend_id);

alter table dev.tpropertyfap
	add constraint fk_propertyfap_agent_id
	foreign key (agent_id) references dev.tagent(agent_id);


\copy dev.tpostcode (postcode_1,name,lat,long) from '../init_data/postcode.dat' with delimiter as ','


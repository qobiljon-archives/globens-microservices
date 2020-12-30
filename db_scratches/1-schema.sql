-- user : i..e, consumer/producer
create table if not exists "gb_user"
(
    -- data
    "id"          serial primary key,
    "email"       text unique,
    "name"        varchar(300),
    "picture"     text         default null,
    "pictureBlob" bytea        default null,
    "tokens"      text,
    "sessionKey"  varchar(300) default null
);


-- business page type : i.e., small, or large business
create type "gb_business_page_type" as enum ('small business', 'large business');
-- business page : i.e., a page where products are created and published
create table if not exists "gb_business_page"
(
    -- data
    "id"          serial primary key,
    "type"        "gb_business_page_type",
    "title"       text,
    "pictureBlob" bytea default null
);


-- product : i.e., the good traded on the platform
create table if not exists "gb_product"
(
    -- data
    "id"               serial primary key,
    "name"             text,
    "published"        boolean default false,
    "pictureBlob"      bytea   default null,
    "price"            float   default 0,
    "currency"         char(3) default 'KRW',
    -- relations
    "business_page_id" integer not null references "gb_business_page" ("id") on delete cascade
);


-- job role : i.e., business owner, employee, or individual entrepreneur
create type "gb_job_role" as enum ('business owner', 'employee', 'individual entrepreneur');
-- job : i.e., jobs in a business page
create table if not exists "gb_job"
(
    -- data
    "id"               serial primary key,
    "role"             gb_job_role,
    "title"            text,
    -- relations
    "user_id"          integer references "gb_user" ("id") default null,
    "business_page_id" integer not null references "gb_business_page" ("id") on delete cascade
);


-- job application : i.e., user's application for a vacancy (empty job position)
create table if not exists "gb_job_application"
(
    -- data
    "id"      serial primary key,
    "message" text,
    -- relations
    "user_id" integer not null references "gb_user" ("id") on delete cascade,
    "job_id"  integer not null references gb_job ("id") on delete cascade,
    -- constraints
    unique ("job_id", "user_id")
);

-- action on product : e.g., create, edit, publish, etc.
create type "gb_job_action" as enum ('create', 'uncreate');
-- product log entry : e.g., created by A, edited by B, published by C, etc.
create table if not exists "gb_job_log"
(
    -- data
    "timestamp" timestamp,
    "action"    gb_job_action,
    -- relations
    "job_id"    integer not null references gb_job ("id") on delete cascade,
    "user_id"   integer references "gb_user" ("id") on delete set null
);


-- purchase log entry : i.e., log of how consumer buys a product from producer
create table if not exists "gb_purchase_log"
(
    -- data
    "id"            serial primary key,
    "purchase_time" timestamp,
    -- relations
    "product_id"    integer not null references "gb_product" ("id") on delete cascade,
    "buyer_id"      integer references "gb_user" ("id") on delete set null,
    -- constraints
    unique ("buyer_id", "product_id")
);


-- action on product : e.g., create, edit, publish, etc.
create type "gb_product_action" as enum ('create', 'uncreate', 'publish', 'unpublish');
-- product log entry : e.g., created by A, edited by B, published by C, etc.
create table if not exists "gb_product_log"
(
    -- data
    "timestamp"  timestamp,
    "action"     "gb_product_action",
    -- relations
    "product_id" integer not null references "gb_product" ("id") on delete cascade,
    "user_id"    integer references "gb_user" ("id") on delete set null
);

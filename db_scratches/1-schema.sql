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
    -- relations
    "business_page_id" integer not null references "gb_business_page" ("id") on delete cascade
);


-- vacancy role : i.e., business owner, employee, or individual entrepreneur
create type "gb_vacancy_role" as enum ('business owner', 'employee', 'individual entrepreneur');
-- vacancy : i.e., jobs in a business page
create table if not exists "gb_vacancy"
(
    -- data
    "id"               serial primary key,
    "role"             "gb_vacancy_role",
    "title"            text,
    -- relations
    "user_id"          integer references "gb_user" ("id") default null,
    "business_page_id" integer not null references "gb_business_page" ("id") on delete cascade
);


-- vacancy application : i.e., user's application for a vacancy
create table if not exists "gb_vacancy_application"
(
    -- data
    "id"         serial primary key,
    -- relations
    "user_id"    integer not null references "gb_user" ("id") on delete cascade,
    "vacancy_id" integer not null references "gb_vacancy" ("id") on delete cascade,
    -- constraints
    unique ("vacancy_id", "user_id")
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
)

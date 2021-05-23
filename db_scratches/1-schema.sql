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
    "sessionKey"  varchar(300) default null,
    "countryCode" varchar(3)   default 'KOR'
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
    "pictureBlob" bytea default null,
    "countryCode" varchar(3)
);


-- product type : i.e., downloadable file, scheduled call, etc.
create type gb_product_type as enum ('downloadable files', 'streamed files', 'scheduled face-to-face meeting', 'scheduled online call');
-- product category : i.e., education, consultation, etc.
create table if not exists "gb_product_category"
(
    -- data
    "id"          serial primary key,
    "name"        varchar(1024),
    "pictureBlob" bytea default null,
    "examples"    varchar(4096)
);
-- product content : i.e., schedule json, stream file, etc.
create table "gb_content"
(
    "id"     serial primary key,
    "title"  text,
    "fileId" text,
    "url"    text
);
-- product : i.e., the good traded on the platform
create table if not exists "gb_product"
(
    -- data
    "id"               serial primary key,
    "name"             text,
    "productType"      gb_product_type,
    "pictureBlob"      bytea             not null,
    "price"            float   default 0,
    "stars"            float8  default 0,
    "reviewsCount"     int     default 0,
    "currency"         char(3) default 'KRW',
    "published"        boolean default false,
    "description"      text,
    "contents"         text,
    -- relations
    "category_id"      integer default 1 not null references "gb_product_category" ("id") on delete cascade,
    "business_page_id" integer           not null references "gb_business_page" ("id") on delete cascade
);
-- publish product requests
create table "gb_product_publish_request"
(
    -- data
    "timestamp"         timestamp,
    "countryCode"       varchar(3),
    -- relations
    "product_id"        int primary key references "gb_product" ("id") on delete cascade,
    "business_page_id"  int references "gb_business_page" ("id") on delete cascade,
    "requester_user_id" int references "gb_user" ("id") on delete cascade
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
    "content" bytea   not null,
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


-- product reviews : e.g., stars, text
create table gb_product_review
(
    -- data
    "id"         serial primary key,
    "stars"      integer,
    "text"       varchar(2056),
    "timestamp"  timestamp,
    -- relations
    "user_id"    integer not null references "gb_user" ("id") on delete cascade,
    "product_id" integer not null references "gb_product" ("id") on delete cascade,
    -- constraints
    unique ("user_id", "product_id")
);

-- employee reviews : i.e., text
create table gb_employee_review
(
    -- data
    "id"               serial primary key,
    "text"             varchar(2056),
    "timestamp"        timestamp,
    -- relations
    "business_page_id" integer not null references "gb_business_page" ("id") on delete cascade,
    "user_id"          integer not null references "gb_user" ("id") on delete cascade,
    "employee_id"      integer not null references "gb_user" ("id") on delete cascade,
    -- constraints
    unique ("user_id", "business_page_id", "employee_id")
);

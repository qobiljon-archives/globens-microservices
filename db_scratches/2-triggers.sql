-- region 1. trigger : un-publish the product once it is modified
-- trigger function for product update --> unpublish product
create or replace function "gb_product_update_procedure"() returns trigger as
$gb_product_update_procedure$
begin
    update "gb_product" set new."published" = false where "id" = new."id";
    return new;
end
$gb_product_update_procedure$ LANGUAGE plpgsql;

drop trigger if exists "gb_check_product_states" on "gb_product";
create trigger "gb_check_product_states"
    after update
    on "gb_product"
    for each row
execute procedure "gb_product_update_procedure"();
-- endregion

-- region 2. trigger : user creation --> business page creation
create or replace function "gb_user_create_procedure"() returns trigger as
$gb_user_create_procedure$
declare
    userId             "gb_user"."id"%type;
    pictureBlob        "gb_user"."pictureBlob"%type;
    businessPageId     "gb_business_page"."id"%type;
    businessOwnerJobId "gb_job"."id"%type;
begin
    -- load new user's details for individual business page
    userId = new."id";
    pictureBlob = new."pictureBlob";

    -- create an individual/small business page
    insert into "gb_business_page"("title", "type", "pictureBlob")
    values (E'Individual entrepreneur\'s page', 'small business', pictureBlob)
    returning "id" into businessPageId;

    -- create business owner job position for the business page
    insert into gb_job("title", "role", "business_page_id")
    values ('Business owner', 'individual entrepreneur', businessPageId)
    returning "id" into businessOwnerJobId;

    -- map the user with the business owner vacancy (empty job position)
    update gb_job set "user_id" = userId where "id" = businessOwnerJobId;

    return new;
end
$gb_user_create_procedure$ language plpgsql;

drop trigger if exists "gb_check_user_creation" on "gb_user";
create trigger "gb_check_user_creation"
    after insert
    on "gb_user"
    for each row
execute procedure "gb_user_create_procedure"();
-- endregion

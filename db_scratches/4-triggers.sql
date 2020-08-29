-- region 1. trigger : un-publish the product once it is modified
-- trigger function for product update --> unpublish product
create function "gb_product_update_procedure"() returns trigger as
$gb_product_update_procedure$
begin
    update "gb_product" set new."published" = false where "id" = new."id";
    return new;
end
$gb_product_update_procedure$ LANGUAGE plpgsql;

create trigger "gb_check_product_states"
    after update
    on "gb_product"
execute procedure "gb_product_update_procedure"();
-- endregion

-- region 2. trigger : user creation --> business page creation
create function "gb_user_create_procedure"() returns trigger as
$gb_user_create_procedure$
declare
    businessPageId         "gb_business_page"."id"%type;
    businessOwnerVacancyId "gb_vacancy"."id"%type;
begin
    -- create an individual/small business page
    insert into "gb_business_page"("title", "type", "pictureBlob")
    values (E'Individual entrepreneur\'s page', 'small business', new."pictureBlob")
    returning "id" into businessPageId;

    -- create business owner vacancy/position for the business page
    insert into "gb_vacancy"("title", "role", "business_page_id")
    values ('Business owner', 'individual entrepreneur', businessPageId)
    returning "id" into businessOwnerVacancyId;

    -- map the user with the business owner vacancy/position
    update "gb_vacancy" set "user_id" = new."id" where "id" = businessOwnerVacancyId;
    return new;
end
$gb_user_create_procedure$ LANGUAGE plpgsql;

create trigger gb_check_user_creation
    after insert
    on "gb_user"
execute procedure "gb_user_create_procedure"();
-- endregion

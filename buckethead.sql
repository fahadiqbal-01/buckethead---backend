DROP TABLE IF EXISTS "public"."folder";
DROP TABLE IF EXISTS "public"."imgpost";
DROP TABLE IF EXISTS "public"."linkpost";
DROP TABLE IF EXISTS "public"."notespost";
DROP TABLE IF EXISTS "public"."users";
-- Table Definition
CREATE TABLE "public"."folder" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "post_id" uuid,
    "user_id" uuid NOT NULL,
    "folder_name" varchar(15) NOT NULL,
    "folder_color" varchar(7) NOT NULL,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."imgpost" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "image_url" text NOT NULL,
    "image_name" varchar(20) NOT NULL,
    "image_note" varchar(50),
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."linkpost" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "image_url" text,
    "link_name" varchar(20) NOT NULL,
    "link_url" text NOT NULL,
    "link_desc" varchar(50),
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."notespost" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "color" varchar(7) NOT NULL,
    "node_title" varchar(20) NOT NULL,
    "note_text" text NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."users" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "name" varchar(20),
    "email" varchar(30) NOT NULL,
    "password_hash" text NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "image_url" text,
    PRIMARY KEY ("id")
);

INSERT INTO "public"."folder" ("id", "post_id", "user_id", "folder_name", "folder_color") VALUES
('9a95375c-a50f-45b0-9fc0-01d2ab4f5ce2', '0680585f-cc5a-46ac-b6f9-d6080eef8db4', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'New space', '#fffff3'),
('c95729ea-105a-4935-8d96-1f894f19d993', 'a753b23c-2be8-43a8-90c4-f66876756940', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'New space', '#fffff3');


INSERT INTO "public"."notespost" ("id", "user_id", "color", "node_title", "note_text", "created_at") VALUES
('0680585f-cc5a-46ac-b6f9-d6080eef8db4', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'white', 't', 'dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd dasdasd ', '2026-09-09 18:09:25.056596'),
('88730887-85ac-4212-add7-41db11fe1439', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'mud', 'hh', 'gdsgggggggggggggggggggggggggggggggggggggggggggggggggggggdsgggggggggggggggggggggggggggggggggggggggggggggggggggggdsgggggggggggggggggggggggggggggggggggggggggggggggggggggdsgggggggggggggggggggggggggggggggggggggggggggggggggggggdsgggggggggggggggggggggggggggggggggggggggggggggggggggggdsgggggggggggggggggggggg', '2026-09-09 18:07:30.418009'),
('a753b23c-2be8-43a8-90c4-f66876756940', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'orange', 'dsssssss', 'sd', '2026-09-10 16:13:21.652988'),
('dab1bd41-a8c7-4dfc-8f94-3ffed1d60081', '3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'blue', 'wre', 'dsf', '2026-09-09 18:03:54.688151');
INSERT INTO "public"."users" ("id", "name", "email", "password_hash", "created_at", "updated_at", "image_url") VALUES
('3a7ed4df-6c3a-4113-a4dc-c4b29f541aec', 'fahad', 'fahadddd.im@gmail.com', '$2b$12$zreg2tExibjroRhVMwHsLeMvsEPHm.9ge9KhVnpjb42Lu0cEQ9MFy', '2026-09-09 17:39:25.063609', '2026-09-09 17:39:25.063609', NULL);


ALTER TABLE "public"."folder" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."imgpost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."linkpost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."notespost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

-- Indices
CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);
CREATE UNIQUE INDEX idx_users_email_unique ON public.users USING btree (email);


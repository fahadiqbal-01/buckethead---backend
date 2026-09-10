DROP TABLE IF EXISTS "public"."users";
DROP TABLE IF EXISTS "public"."imgpost";
DROP TABLE IF EXISTS "public"."linkpost";
DROP TABLE IF EXISTS "public"."notespost";
DROP TABLE IF EXISTS "public"."folder";
-- Table Definition
CREATE TABLE "public"."users" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "name" varchar(20),
    "email" varchar(30) NOT NULL,
    "password_hash" text NOT NULL,
    "image_url" text,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."imgpost" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "image_url" text NOT NULL,
    "image_name" varchar(20) NOT NULL,
    "image_note" varchar(50),
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
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."notespost" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "user_id" uuid NOT NULL,
    "color" varchar(7) NOT NULL,
    "node_title" varchar(20) NOT NULL,
    "note_text" text NOT NULL,
    PRIMARY KEY ("id")
);

-- Table Definition
CREATE TABLE "public"."folder" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "post_id" uuid,
    "user_id" uuid NOT NULL,
    "folder_name" varchar(15) NOT NULL,
    "folder_color" varchar(7) NOT NULL,
    PRIMARY KEY ("id")
);

INSERT INTO "public"."users" ("id", "name", "email", "password_hash", "created_at", "updated_at") VALUES
('1a512ddb-d2ba-4921-8b63-05e490ac135d', 'fahad', 'fahad@gmail.com', '$2b$12$Y.bfoBLifhTeiAbMAe1TbOBnEkV4uLn2rbvEAnQAS0ShI2Gnnq9Hi', '2026-08-29 15:54:37.703106', '2026-08-29 15:54:37.703106'),
('3ab19800-f0c5-42be-902e-065ef921d8bb', 'fahadd', 'fahadd@gmail.com', '$2b$12$NBeYTB5ptm24xuPDnX3mSeqzUWbjrL.ZhijBznfoWaYDSOVPa2Tsy', '2026-08-29 15:54:49.679524', '2026-08-29 15:54:49.679524'),
('3cf6a9eb-1c4f-414a-be15-ba1e75e97acb', 'dd', 'dd@gmail.com', '$2b$12$.rmeG345uZFm1g3wY1BGyuL9PK5i7SS3YuCUykiv00szcEaUGAiGW', '2026-08-30 20:03:57.237601', '2026-08-30 20:03:57.237601');
INSERT INTO "public"."imgpost" ("id", "user_id", "image_url", "image_name", "image_note") VALUES
('370aa2ac-3039-4b23-9697-b64919401ec5', '3cf6a9eb-1c4f-414a-be15-ba1e75e97acb', 'https://res.cloudinary.com/dnm3tmkca/image/upload/v1788194672/rymp4ioi0verqpk7mkkw.png', 'DUMP (1).png', 'dfdf');





-- Indices
CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);
CREATE UNIQUE INDEX idx_users_email_unique ON public.users USING btree (email);

ALTER TABLE "public"."imgpost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."linkpost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."notespost" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;

ALTER TABLE "public"."folder" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


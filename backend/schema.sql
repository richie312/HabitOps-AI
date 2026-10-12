CREATE DATABASE IF NOT EXISTS habitops CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE habitops;

CREATE TABLE IF NOT EXISTS activities (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 client_id CHAR(36) NULL,
 activity_type VARCHAR(32) NOT NULL,
 start_at DATETIME(6) NOT NULL, end_at DATETIME(6) NOT NULL,
 duration_minutes DECIMAL(12,4) NOT NULL, distance_km DECIMAL(12,4) NULL,
 notes TEXT NULL, steps INT UNSIGNED NULL, workout_type VARCHAR(100) NULL,
 completed BOOLEAN NOT NULL DEFAULT TRUE, average_speed_kmh DECIMAL(12,4) NULL,
 average_pace_min_per_km DECIMAL(12,4) NULL, drum_practice_type VARCHAR(100) NULL,
 created_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)), updated_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)),
 UNIQUE KEY uq_activities_client_id (client_id), INDEX ix_activities_type_start (activity_type,start_at DESC)
) ENGINE=InnoDB;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS client_id CHAR(36) NULL;

CREATE TABLE IF NOT EXISTS activity_route_points (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, activity_id BIGINT UNSIGNED NOT NULL,
 sequence_number INT UNSIGNED NOT NULL, latitude DECIMAL(10,7) NOT NULL, longitude DECIMAL(10,7) NOT NULL,
 recorded_at DATETIME(6) NOT NULL, accuracy DECIMAL(10,3) NULL,
 UNIQUE KEY uq_activity_route_sequence (activity_id,sequence_number),
 CONSTRAINT fk_route_activity FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vitals (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, client_id CHAR(36) NULL,
 recorded_at DATETIME(6) NOT NULL, systolic SMALLINT UNSIGNED NOT NULL, diastolic SMALLINT UNSIGNED NOT NULL,
 glucose DECIMAL(8,2) NOT NULL, pulse SMALLINT UNSIGNED NOT NULL, spo2 DECIMAL(5,2) NOT NULL, weight DECIMAL(8,2) NOT NULL,
 created_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)), updated_at DATETIME(6) NOT NULL DEFAULT (UTC_TIMESTAMP(6)),
 UNIQUE KEY uq_vitals_client_id (client_id), INDEX ix_vitals_recorded_at (recorded_at DESC)
) ENGINE=InnoDB;
ALTER TABLE vitals ADD COLUMN IF NOT EXISTS client_id CHAR(36) NULL;

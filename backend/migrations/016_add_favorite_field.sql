-- Migration: Add favorite field to gear_containers table
-- This migration adds the favorite field to gear_containers table for marking favorite containers.

-- Add favorite field to gear_containers
ALTER TABLE gear_containers 
ADD COLUMN IF NOT EXISTS favorite BOOLEAN NOT NULL DEFAULT FALSE;

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS ix_gear_containers_favorite 
ON gear_containers(favorite);

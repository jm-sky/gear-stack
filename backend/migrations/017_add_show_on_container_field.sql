-- Migration: Add show_on_container field to gear_items table
-- This migration adds the show_on_container field to gear_items table for controlling
-- whether item images should be displayed in container view gallery.

-- Add show_on_container field to gear_items
ALTER TABLE gear_items 
ADD COLUMN IF NOT EXISTS show_on_container BOOLEAN NOT NULL DEFAULT FALSE;

-- Add index for better query performance when filtering items by show_on_container
CREATE INDEX IF NOT EXISTS ix_gear_items_show_on_container 
ON gear_items(show_on_container);


-- Migration: Add gear_containers and gear_items tables
-- Created: 2025-11-19
-- Description: Creates tables for gear management system

-- Create gear_containers table
CREATE TABLE gear_containers (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    color VARCHAR(20) DEFAULT 'default',
    parent_container_id VARCHAR(36),
    brand VARCHAR(255),
    price FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_container_id) REFERENCES gear_containers(id) ON DELETE SET NULL
);

-- Create indexes for gear_containers
CREATE INDEX ix_gear_containers_user_id ON gear_containers(user_id);

-- Create gear_items table
CREATE TABLE gear_items (
    id VARCHAR(36) PRIMARY KEY,
    container_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    weight FLOAT NOT NULL,
    weight_unit VARCHAR(5) NOT NULL DEFAULT 'g',
    notes TEXT,
    expiration_date TIMESTAMP WITH TIME ZONE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'owned',
    nested_container_id VARCHAR(36),
    price FLOAT,
    url TEXT,
    brand VARCHAR(255),
    color VARCHAR(50),
    quality VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (container_id) REFERENCES gear_containers(id) ON DELETE CASCADE,
    FOREIGN KEY (nested_container_id) REFERENCES gear_containers(id) ON DELETE SET NULL
);

-- Create indexes for gear_items
CREATE INDEX ix_gear_items_container_id ON gear_items(container_id);

-- SQLite compatibility notes:
-- For SQLite, replace:
-- - TIMESTAMP WITH TIME ZONE -> DATETIME
-- - FLOAT -> REAL
-- - Remove "WITH TIME ZONE" from timestamp fields

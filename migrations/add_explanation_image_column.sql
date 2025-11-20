-- Migration: Add explanation_image column to questions table
-- Date: 2025-11-09
-- Description: Adds optional explanation_image field to store image URLs/paths for visual explanations

-- Add the new column (nullable, as it's optional)
ALTER TABLE questions 
ADD COLUMN IF NOT EXISTS explanation_image VARCHAR(255) NULL;

-- Add comment to document the column
COMMENT ON COLUMN questions.explanation_image IS 'Optional image URL/path for visual explanations when text alone is insufficient';

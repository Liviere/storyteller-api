-- Initialize the storyteller database
-- This script runs automatically when MySQL container starts for the first time

-- Set charset and collation
ALTER DATABASE storyteller CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create an additional user for application (if needed)
-- GRANT ALL PRIVILEGES ON storyteller.* TO 'storyteller_user'@'%';
-- FLUSH PRIVILEGES;

-- Optional: Create some initial data or configurations
-- INSERT INTO stories (title, content, author, genre, is_published) VALUES 
-- ('Welcome Story', 'Welcome to the Story Teller API!', 'System', 'Info', true);

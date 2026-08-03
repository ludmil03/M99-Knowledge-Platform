-- =====================================================
-- M99 KNOWLEDGE PLATFORM
-- DATABASE VERSION 0.1
-- =====================================================

CREATE DATABASE IF NOT EXISTS m99_knowledge
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE m99_knowledge;

-- =====================================================
-- BRANDS
-- =====================================================

CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    website VARCHAR(255),
    description TEXT,
    status ENUM('draft','review','approved') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- COLLECTIONS
-- =====================================================

CREATE TABLE collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    code VARCHAR(100) UNIQUE,
    name VARCHAR(255),
    description TEXT,
    FOREIGN KEY (brand_id) REFERENCES brands(id)
);

-- =====================================================
-- PRODUCTS
-- =====================================================

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,

    sku VARCHAR(100) UNIQUE NOT NULL,

    manufacturer_sku VARCHAR(100),

    brand_id INT NOT NULL,

    collection_id INT,

    name VARCHAR(255),

    category VARCHAR(255),

    gender VARCHAR(50),

    status ENUM('draft','review','approved') DEFAULT 'draft',

    knowledge_score DECIMAL(5,2) DEFAULT 0,

    trust_score DECIMAL(5,2) DEFAULT 0,

    seo_score DECIMAL(5,2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id)
        REFERENCES brands(id),

    FOREIGN KEY (collection_id)
        REFERENCES collections(id)
);

-- =====================================================
-- TECHNOLOGIES
-- =====================================================

CREATE TABLE technologies (

    id INT AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(100) UNIQUE,

    name VARCHAR(255),

    description TEXT,

    source VARCHAR(255),

    status ENUM('draft','review','approved') DEFAULT 'draft'
);

-- =====================================================
-- PRODUCT TECHNOLOGIES
-- =====================================================

CREATE TABLE product_technologies (

    product_id INT,

    technology_id INT,

    PRIMARY KEY(product_id,technology_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(technology_id)
        REFERENCES technologies(id)
);

-- =====================================================
-- MATERIALS
-- =====================================================

CREATE TABLE materials (

    id INT AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(100) UNIQUE,

    name VARCHAR(255),

    description TEXT
);

-- =====================================================
-- PRODUCT MATERIALS
-- =====================================================

CREATE TABLE product_materials (

    product_id INT,

    material_id INT,

    position VARCHAR(100),

    PRIMARY KEY(product_id,material_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(material_id)
        REFERENCES materials(id)
);

-- =====================================================
-- STANDARDS
-- =====================================================

CREATE TABLE standards (

    id INT AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(100) UNIQUE,

    title VARCHAR(255),

    description TEXT
);

-- =====================================================
-- PRODUCT STANDARDS
-- =====================================================

CREATE TABLE product_standards (

    product_id INT,

    standard_id INT,

    PRIMARY KEY(product_id,standard_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(standard_id)
        REFERENCES standards(id)
);

-- =====================================================
-- RISKS
-- =====================================================

CREATE TABLE risks (

    id INT AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(100),

    name VARCHAR(255),

    description TEXT
);

-- =====================================================
-- PRODUCT RISKS
-- =====================================================

CREATE TABLE product_risks (

    product_id INT,

    risk_id INT,

    PRIMARY KEY(product_id,risk_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(risk_id)
        REFERENCES risks(id)
);

-- =====================================================
-- PROFESSIONS
-- =====================================================

CREATE TABLE professions (

    id INT AUTO_INCREMENT PRIMARY KEY,

    code VARCHAR(100),

    name VARCHAR(255),

    description TEXT
);

-- =====================================================
-- PRODUCT PROFESSIONS
-- =====================================================

CREATE TABLE product_professions (

    product_id INT,

    profession_id INT,

    PRIMARY KEY(product_id,profession_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(profession_id)
        REFERENCES professions(id)
);

-- =====================================================
-- KNOWLEDGE SOURCES
-- =====================================================

CREATE TABLE knowledge_sources (

    id INT AUTO_INCREMENT PRIMARY KEY,

    source_type VARCHAR(100),

    title VARCHAR(255),

    url TEXT,

    trust_level INT,

    access_date DATE
);

-- =====================================================
-- PRODUCT SOURCES
-- =====================================================

CREATE TABLE product_sources (

    product_id INT,

    source_id INT,

    PRIMARY KEY(product_id,source_id),

    FOREIGN KEY(product_id)
        REFERENCES products(id),

    FOREIGN KEY(source_id)
        REFERENCES knowledge_sources(id)
);

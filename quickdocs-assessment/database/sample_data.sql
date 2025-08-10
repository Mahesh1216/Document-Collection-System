-- Sample Processes
INSERT INTO processes (name, description, status) VALUES
('Home Loan Application', 'Process for applying for a home loan.', 'active'),
('KYC Verification', 'Know Your Customer verification process.', 'active');

-- Sample Document Types
INSERT INTO document_types (name, description, required_fields) VALUES
('PAN Card', 'Permanent Account Number card.', '{"pan_number": "text"}'),
('Aadhaar Card', 'Aadhaar card for identity verification.', '{"aadhaar_number": "text"}'),
('Salary Slip', 'Latest salary slip.', '{"monthly_salary": "number", "company_name": "text"}'),
('Bank Statement', 'Last 6 months bank statement.', '{"account_number": "text", "bank_name": "text"}'),
('Photo', 'Passport size photograph.', '{"face_clarity": "text"}');

-- Sample Customers
INSERT INTO customers (name, email, phone) VALUES
('Rajesh Sharma', 'rajesh.sharma@example.com', '9876543210'),
('Priya Patel', 'priya.patel@example.com', '9876543211'),
('Amit Singh', 'amit.singh@example.com', '9876543212'),
('Sunita Gupta', 'sunita.gupta@example.com', '9876543213'),
('Vikram Reddy', 'vikram.reddy@example.com', '9876543214');

-- Sample Process Document Requirements
-- Home Loan Application: PAN + Salary Slip + Bank Statement
INSERT INTO process_document_requirements (process_id, document_type_id, is_mandatory) VALUES
(1, 1, 1), -- PAN Card
(1, 3, 1), -- Salary Slip
(1, 4, 1); -- Bank Statement

-- KYC Verification: PAN + Aadhaar
INSERT INTO process_document_requirements (process_id, document_type_id, is_mandatory) VALUES
(2, 1, 1), -- PAN Card
(2, 2, 1); -- Aadhaar

-- Sample Process Assignments
INSERT INTO process_assignments (customer_id, process_id, status, completion_percentage) VALUES
(1, 1, 'pending', 33.3),
(2, 1, 'completed', 100),
(3, 2, 'pending', 50),
(4, 2, 'completed', 100),
(5, 1, 'pending', 0);

-- Sample Document Submissions
-- Rajesh Sharma (Home Loan) - PAN submitted
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status) VALUES
(1, 1, 1, '/uploads/rajesh_pan.pdf', '{"pan_number": "ABCDE1234F"}', 'approved');

-- Priya Patel (Home Loan) - All documents submitted
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status) VALUES
(2, 1, 1, '/uploads/priya_pan.pdf', '{"pan_number": "FGHIJ5678K"}', 'approved'),
(2, 1, 3, '/uploads/priya_salary.pdf', '{"monthly_salary": 80000, "company_name": "QuickDocs"}', 'approved'),
(2, 1, 4, '/uploads/priya_bank.pdf', '{"account_number": "1234567890", "bank_name": "Example Bank"}', 'approved');

-- Amit Singh (KYC) - PAN submitted
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status) VALUES
(3, 2, 1, '/uploads/amit_pan.pdf', '{"pan_number": "KLMNO9012P"}', 'approved');

-- Sunita Gupta (KYC) - All documents submitted
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data, validation_status) VALUES
(4, 2, 1, '/uploads/sunita_pan.pdf', '{"pan_number": "QRSTU3456V"}', 'approved'),
(4, 2, 2, '/uploads/sunita_aadhaar.pdf', '{"aadhaar_number": "1234 5678 9012"}', 'approved');

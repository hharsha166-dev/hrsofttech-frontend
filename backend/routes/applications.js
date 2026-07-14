const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/db');
const { requireAuth, requireRole } = require('../middleware/auth');

const router = express.Router();

const PDF_ENGINE_DIR = path.join(__dirname, '..', 'pdf_engine');
const TEMPLATES_DIR = path.join(__dirname, '..', 'pdf_templates');
const GENERATED_DIR = path.join(__dirname, '..', 'generated_pdfs');
if (!fs.existsSync(GENERATED_DIR)) fs.mkdirSync(GENERATED_DIR, { recursive: true });

const TEMPLATE_BY_TYPE = {
  new_pan: path.join(TEMPLATES_DIR, 'form93.pdf'),
  correction: path.join(TEMPLATES_DIR, 'correction.pdf'),
};

/**
 * Fills the official NSDL-style PDF (Form 93 or the correction form) with
 * this application's data by shelling out to the Python field-mapping
 * engine in pdf_engine/. Resolves with the output file path, or rejects
 * with a message safe to show the retailer.
 */
function generateFilledPdf(application) {
  return new Promise((resolve, reject) => {
    const template = TEMPLATE_BY_TYPE[application.application_type];
    if (!template) return reject(new Error('Unknown application type'));

    const outputPath = path.join(GENERATED_DIR, `${application.id}.pdf`);
    const child = execFile(
      'python3',
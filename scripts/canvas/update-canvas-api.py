#!/usr/bin/env python3
"""
Simple API endpoint for updating Canvas from DOCX tracked changes.
Can be run as a local server or used with serverless functions.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for GitHub Pages

UPDATE_SCRIPT = Path(__file__).parent / "update-canvas-from-docx.py"

@app.route('/update-canvas-api', methods=['POST'])
def update_canvas():
    """Handle update canvas request."""
    try:
        data = request.json
        box_file_id = data.get('box_file_id')
        canvas_page_slug = data.get('canvas_page_slug')
        page_name = data.get('page_name')

        if not all([box_file_id, canvas_page_slug]):
            return jsonify({
                'success': False,
                'message': 'Missing required parameters: box_file_id, canvas_page_slug'
            }), 400

        # Run the update script with environment variables
        import os
        env = os.environ.copy()
        # Pass Box token if available
        box_token = os.getenv('BOX_DEVELOPER_TOKEN')
        if box_token:
            env['BOX_DEVELOPER_TOKEN'] = box_token

        result = subprocess.run(
            [
                'python3',
                str(UPDATE_SCRIPT),
                '--box-file-id', box_file_id,
                '--canvas-page-slug', canvas_page_slug
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env  # Pass environment to subprocess
        )

        if result.returncode == 0:
            # Parse JSON output from script
            try:
                output = json.loads(result.stdout)
                return jsonify(output)
            except json.JSONDecodeError:
                # If output isn't JSON, return success with stdout
                return jsonify({
                    'success': True,
                    'message': result.stdout.strip() or 'Canvas updated successfully',
                    'timestamp': __import__('datetime').datetime.now().isoformat()
                })
        else:
            return jsonify({
                'success': False,
                'message': f'Update failed: {result.stderr}'
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Update timed out after 5 minutes'
        }), 504
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Run on localhost for development
    app.run(host='127.0.0.1', port=5000, debug=True)


class PodcastMapper {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.cy = null;
        this.currentEpisodeId = null;
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadEpisodes();
    }
    
    initializeElements() {
        this.episodeSelect = document.getElementById('episodeSelect');
        this.loadGraphBtn = document.getElementById('loadGraphBtn');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.uploadModal = document.getElementById('uploadModal');
        this.uploadForm = document.getElementById('uploadForm');
        this.sidebar = document.getElementById('sidebar');
        this.entityDetails = document.getElementById('entityDetails');
        this.loading = document.getElementById('loading');
    }
    
    setupEventListeners() {
        this.loadGraphBtn.addEventListener('click', () => this.loadGraph());
        this.uploadBtn.addEventListener('click', () => this.showUploadModal());
        this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        
        // Modal controls
        document.querySelector('.close').addEventListener('click', () => this.hideUploadModal());
        document.getElementById('cancelUpload').addEventListener('click', () => this.hideUploadModal());
        
        // Close modal when clicking outside
        this.uploadModal.addEventListener('click', (e) => {
            if (e.target === this.uploadModal) {
                this.hideUploadModal();
            }
        });
    }
    
    async loadEpisodes() {
        try {
            const response = await fetch(`${this.apiBase}/episodes`);
            const episodes = await response.json();
            
            this.episodeSelect.innerHTML = '<option value="">Select an episode...</option>';
            episodes.forEach(episode => {
                const option = document.createElement('option');
                option.value = episode.id;
                option.textContent = `${episode.title} (${episode.status})`;
                this.episodeSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading episodes:', error);
            this.showError('Failed to load episodes');
        }
    }
    
    async loadGraph() {
        const episodeId = this.episodeSelect.value;
        if (!episodeId) {
            alert('Please select an episode first');
            return;
        }
        
        this.currentEpisodeId = episodeId;
        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBase}/episodes/${episodeId}/graph`);
            const graphData = await response.json();
            
            this.renderGraph(graphData);
        } catch (error) {
            console.error('Error loading graph:', error);
            this.showError('Failed to load graph data');
        } finally {
            this.showLoading(false);
        }
    }
    
    renderGraph(data) {
        // Initialize Cytoscape
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            
            elements: [
                // Nodes
                ...data.nodes.map(node => ({
                    data: {
                        id: node.id,
                        label: node.label,
                        type: node.type,
                        summary: node.summary
                    }
                })),
                // Edges
                ...data.edges.map(edge => ({
                    data: {
                        id: edge.id,
                        source: edge.source,
                        target: edge.target,
                        label: edge.label
                    }
                }))
            ],
            
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': (ele) => this.getNodeColor(ele.data('type')),
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#fff',
                        'text-outline-width': 2,
                        'text-outline-color': '#000',
                        'font-size': '12px',
                        'width': 60,
                        'height': 60
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 4,
                        'line-color': '#888',
                        'target-arrow-color': '#888',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -10,
                        'text-valign': 'top'
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 3,
                        'border-color': '#667eea'
                    }
                },
                {
                    selector: '.highlighted',
                    style: {
                        'background-color': '#667eea',
                        'line-color': '#667eea',
                        'target-arrow-color': '#667eea',
                        'transition-property': 'background-color, line-color, target-arrow-color',
                        'transition-duration': '0.2s'
                    }
                }
            ],
            
            layout: {
                name: 'dagre',
                padding: 30,
                spacingFactor: 1.75,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            }
        });
        
        // Add click event for nodes
        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            this.showEntityDetails(node.data());

            this.cy.elements().removeClass('highlighted');
            node.addClass('highlighted');
            node.neighborhood().addClass('highlighted');
        });

        this.cy.on('tap', (evt) => {
            if (evt.target === this.cy) {
                this.cy.elements().removeClass('highlighted');
            }
        });
    }
    
    getNodeColor(type) {
        const colors = {
            'Person': '#e74c3c',
            'Organization': '#3498db',
            'Event': '#f39c12',
            'Concept': '#9b59b6',
            'Source Material': '#2ecc71'
        };
        return colors[type] || '#95a5a6';
    }
    
    async showEntityDetails(nodeData) {
        try {
            const response = await fetch(`${this.apiBase}/entities/${nodeData.id}/details`);
            const entityData = await response.json();
            
            const entity = entityData.entity;
            const details = entityData.details;
            
            let html = `
                <div class="entity-info">
                    <div class="entity-name">${entity.name}</div>
                    <div class="entity-type">${entity.type}</div>
                    ${entity.summary ? `<div class="entity-summary">${entity.summary}</div>` : ''}
                </div>
            `;
            
            if (details.length > 0) {
                html += '<div class="details-section"><h4>Details:</h4>';
                details.forEach(detail => {
                    const timestamp = this.formatTimestamp(detail.timestamp_start);
                    html += `
                        <div class="detail-item">
                            <div class="detail-text">${detail.detail}</div>
                            <div class="detail-timestamp" onclick="app.jumpToTimestamp(${detail.timestamp_start})">
                                ${timestamp}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            this.entityDetails.innerHTML = html;
        } catch (error) {
            console.error('Error loading entity details:', error);
            this.entityDetails.innerHTML = '<p>Error loading entity details</p>';
        }
    }
    
    formatTimestamp(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    jumpToTimestamp(seconds) {
        // This would be implemented to jump to the specific timestamp in the audio
        // For now, just show an alert
        alert(`Would jump to timestamp: ${this.formatTimestamp(seconds)}`);
    }
    
    showUploadModal() {
        this.uploadModal.classList.remove('hidden');
    }
    
    hideUploadModal() {
        this.uploadModal.classList.add('hidden');
        this.uploadForm.reset();
        document.getElementById('uploadProgress').classList.add('hidden');
    }
    
    async handleUpload(e) {
        e.preventDefault();
        
        const title = document.getElementById('episodeTitle').value;
        const url = document.getElementById('episodeUrl').value;
        const audioFile = document.getElementById('audioFile').files[0];
        
        if (!audioFile) {
            alert('Please select an audio file');
            return;
        }
        
        try {
            // First create the episode
            const formData = new FormData();
            formData.append('title', title);
            if (url) formData.append('episode_url', url);
            
            const episodeResponse = await fetch(`${this.apiBase}/episodes`, {
                method: 'POST',
                body: formData
            });
            
            if (!episodeResponse.ok) {
                const errorData = await episodeResponse.json();
                throw new Error(errorData.detail || 'Failed to create episode');
            }
            
            const episodeData = await episodeResponse.json();
            const episodeId = episodeData.episode_id;
            
            // Show progress
            document.getElementById('uploadProgress').classList.remove('hidden');
            document.getElementById('progressText').textContent = 'Processing audio...';
            
            // Upload and process the audio file
            const audioFormData = new FormData();
            audioFormData.append('audio_file', audioFile);
            
            const processResponse = await fetch(`${this.apiBase}/episodes/${episodeId}/process`, {
                method: 'POST',
                body: audioFormData
            });
            
            if (processResponse.ok) {
                const result = await processResponse.json();
                alert(`Successfully processed ${result.chunks_processed} audio chunks!`);
                this.hideUploadModal();
                this.loadEpisodes(); // Refresh episode list
            } else {
                const error = await processResponse.json();
                throw new Error(error.detail || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            alert(`Upload failed: ${error.message}`);
        }
    }
    
    showLoading(show) {
        if (show) {
            this.loading.classList.remove('hidden');
        } else {
            this.loading.classList.add('hidden');
        }
    }
    
    showError(message) {
        alert(message); // Simple error handling for MVP
    }
}

// Initialize the application
const app = new PodcastMapper();
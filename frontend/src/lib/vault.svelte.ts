export const vault = new (class ValutState {
	selected_files: File[] = $state([]);
	server_files: any[] = $state([]);
	uploading = $state(false);
	dragging = $state(false);
	error = $state('');

	file_to_delete: { id: number; filename: string } | null = $state(null);
	is_delete_modal_open = $state(false);

	total_size = $derived(this.server_files.reduce((acc, file) => acc + file.size, 0));

	add_files(files: FileList | File[]) {
		this.selected_files = [...this.selected_files, ...Array.from(files)];
	}

	remove_file(index: number) {
		this.selected_files.splice(index, 1);
	}

	clear_state() {
		this.selected_files = [];
		this.server_files = [];
		this.error = '';
	}

	async fetch_files() {
		const token = localStorage.getItem('vault_token');
		if (!token) return;

		try {
			const resp = await fetch('http://localhost:8000/files', {
				method: 'GET',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (resp.ok) {
				const data = await resp.json();
				this.server_files = data.files;
			}
		} catch (err: any) {
			console.error('Error fetching files:', err);
		}
	}

	async upload_files() {
		if (this.selected_files.length === 0) return;

		this.uploading = true;
		this.error = '';

		const token = localStorage.getItem('vault_token');
		if (!token) return;

		const form_data = new FormData();
		for (const file of this.selected_files) {
			form_data.append('files', file);
		}

		try {
			const resp = await fetch('http://localhost:8000/files', {
				method: 'POST',
				headers: { Authorization: `Bearer ${token}` },
				body: form_data
			});

			if (!resp.ok) throw new Error('Failed to upload files');

			this.selected_files = [];
			await this.fetch_files();
		} catch (err: any) {
			console.error('Upload error:', err);
			this.error = err.message || 'Server error during upload';
		} finally {
			this.uploading = false;
		}
	}

	async trigger_download(id: number, filename: string) {
		const token = localStorage.getItem('vault_token');
		if (!token) return;

		try {
			const resp = await fetch(`http://localhost:8000/file/${id}`, {
				method: 'GET',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (!resp.ok) throw new Error('Download failed');

			const blob = await resp.blob();
			const url = window.URL.createObjectURL(blob);

			const a = document.createElement('a');
			a.style.display = 'none';
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();

			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		} catch (err) {
			console.error('Download error:', err);
			alert('Failed to download file.');
		}
	}

	request_delete(id: number, filename: string) {
		this.file_to_delete = { id, filename };
		this.is_delete_modal_open = true;
	}

	async confirm_delete() {
		if (!this.file_to_delete) return;

		const token = localStorage.getItem('vault_token');
		if (!token) return;

		try {
			const response = await fetch(`http://localhost:8000/file/${this.file_to_delete.id}`, {
				method: 'DELETE',
				headers: { Authorization: `Bearer ${token}` }
			});

			if (!response.ok) {
				const errData = await response.json();
				throw new Error(errData.detail || 'Failed to delete file');
			}

			await this.fetch_files();
		} catch (err: any) {
			console.error('Delete error:', err);
			alert(err.message);
		} finally {
			this.is_delete_modal_open = false;
			this.file_to_delete = null;
		}
	}
})();

export const auth = new (class AuthState {
	logged_in = $state(false);
	username = $state('');
	error = $state('');

	async login(user: string, pass: string): Promise<boolean> {
		if (this.logged_in) return true;
		if (!user.trim() || !pass.trim()) {
			this.error = 'Missing username or password';
			setTimeout(() => (this.error = ''), 2500);
			return false;
		}

		try {
			const resp = await fetch('http://localhost:8000/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: user, password: pass })
			});

			if (!resp.ok) {
				const err_data = await resp.json();
				throw new Error(err_data.detail || 'Login failed');
			}

			const data = await resp.json();
			localStorage.setItem('vault_token', data.access_token);

			this.username = user;
			this.logged_in = true;
			return true;
		} catch (err: any) {
			console.error('Login error:', err);
			this.error = err.message || 'Could not connect to server';
			setTimeout(() => (this.error = ''), 2500);
			return false;
		}
	}

	logout() {
		localStorage.removeItem('vault_token');
		this.logged_in = false;
		this.username = '';
	}

	async check_session(): Promise<boolean> {
		const token = localStorage.getItem('vault_token');
		if (!token) return false;

		try {
			const resp = await fetch('http://localhost:8000/me', {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (resp.ok) {
				const data = await resp.json();
				this.username = data.username;
				this.logged_in = true;
				return true;
			} else {
				this.logout();
				return false;
			}
		} catch (err: any) {
			console.error('Error verifying token:', err);
			return false;
		}
	}
})();

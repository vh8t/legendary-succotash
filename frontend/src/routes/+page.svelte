<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { Input } from '$lib/components/ui/input';
	import { Badge } from '$lib/components/ui/badge';

	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import * as Card from '$lib/components/ui/card';
	import * as Table from '$lib/components/ui/table';

	import { CloudUpload, FileText, X, Download } from '@lucide/svelte';

	import { auth } from '$lib/login.svelte';
	import { vault } from '$lib/vault.svelte';

	import { onMount } from 'svelte';

	let login_user: string = $state('');
	let login_pass: string = $state('');
	let file_input: HTMLInputElement | null = $state(null);

	const format_bytes = (bytes: number) => {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	};

	onMount(async () => {
		const dark_mode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
		if (dark_mode && dark_mode.matches) document.documentElement.classList.add('dark');
		if (await auth.check_session()) vault.fetch_files();
	});

	const handle_login_submit = async (e: Event) => {
		e.preventDefault();
		if (await auth.login(login_user, login_pass)) {
			login_pass = '';
			vault.fetch_files();
		}
	};

	const handle_logout_click = () => {
		auth.logout();
		vault.clear_state();
	};

	const handle_dragover = (e: DragEvent) => {
		e.preventDefault();
		vault.dragging = true;
	};

	const handle_dragleave = () => {
		vault.dragging = false;
	};

	const handle_drop = (e: DragEvent) => {
		e.preventDefault();
		vault.dragging = false;
		if (e.dataTransfer?.files) vault.add_files(e.dataTransfer.files);
	};

	const handle_file_select = (e: Event) => {
		const target = e.target as HTMLInputElement;
		if (target.files) vault.add_files(target.files);
		target.value = '';
	};
</script>

{#if !auth.logged_in}
	<div class="flex min-h-screen flex-col items-center justify-center">
		<h1 class="scroll-m-20 pb-8 text-4xl font-extrabold tracking-tight text-balance">LocalVault</h1>
		<Card.Root class="w-full max-w-sm">
			<Card.Header>
				<Card.Title>Login to your account</Card.Title>
			</Card.Header>
			<form onsubmit={handle_login_submit}>
				<Card.Content>
					<div class="flex flex-col gap-6">
						<div class="grid gap-2">
							<Label for="username">Username</Label>
							<Input
								class={auth.error && !login_user ? 'border-red-500' : ''}
								id="username"
								placeholder="user"
								bind:value={login_user}
								autocomplete="username"
							/>
						</div>
						<div class="grid gap-2">
							<Label for="password">Password</Label>
							<Input
								class={auth.error && !login_pass ? 'border-red-500' : ''}
								id="password"
								type="password"
								bind:value={login_pass}
								autocomplete="current-password"
							/>
						</div>
					</div>
				</Card.Content>
				<Card.Footer class="flex-col gap-2 pt-7">
					<Button type="submit" class="w-full cursor-pointer">Login</Button>
					{#if auth.error}
						<p class="text-xs text-red-500">{auth.error}</p>
					{/if}
				</Card.Footer>
			</form>
		</Card.Root>
	</div>
{:else}
	<div class="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-8 p-6 pt-12">
		<div class="flex items-center justify-between border-b pb-4">
			<div>
				<h1 class="text-3xl font-bold tracking-tight">LocalVault</h1>
				<p class="mt-1 text-sm text-muted-foreground">
					Logged in as <span class="font-semibold text-foreground">{auth.username}</span>
				</p>
			</div>
			<Button class="cursor-pointer" variant="outline" size="sm" onclick={handle_logout_click}
				>Logout</Button
			>
		</div>

		<button
			class="flex cursor-pointer flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-12 transition-all duration-200
      {vault.dragging
				? 'scale-[1.02] border-primary bg-primary/5'
				: 'border-muted-foreground/20 hover:border-muted-foreground/40 hover:bg-muted/30'}"
			ondragover={handle_dragover}
			ondragleave={handle_dragleave}
			ondrop={handle_drop}
			onclick={() => file_input!.click()}
		>
			<div class="pointer-events-none flex flex-col items-center gap-3">
				<div class="rounded-full bg-muted p-4">
					<CloudUpload class="text-muted-foreground" size={32} strokeWidth={2} />
				</div>
				<div class="text-center">
					<p class="text-lg font-medium">Drag and drop files here</p>
					<p class="text-sm text-muted-foreground">or click to browse your computer</p>
				</div>
			</div>
		</button>

		<input
			type="file"
			multiple
			class="hidden"
			bind:this={file_input}
			onchange={handle_file_select}
		/>

		{#if vault.selected_files.length > 0}
			<div class="flex animate-in flex-col gap-4 fade-in slide-in-from-bottom-4">
				<h2 class="border-b pb-2 text-lg font-semibold">Ready to upload</h2>
				<div class="flex flex-col gap-2">
					{#each vault.selected_files as file, i}
						<Card.Root class="py-2 transition-all hover:shadow-sm">
							<Card.Content class="flex items-center justify-between py-2">
								<div class="flex items-center gap-3 overflow-hidden">
									<FileText class="shrink-0 text-muted-foreground" size={16} strokeWidth={2} />
									<span class="truncate text-sm font-medium">{file.name}</span>
								</div>
								<div class="ml-4 flex shrink-0 items-center gap-4">
									<span class="text-xs text-muted-foreground">{format_bytes(file.size)}</span>
									<Button
										variant="ghost"
										size="icon"
										class="h-8 w-8 cursor-pointer text-muted-foreground hover:text-destructive"
										onclick={() => vault.remove_file(i)}
									>
										<X size={16} strokeWidth={2} />
									</Button>
								</div>
							</Card.Content>
						</Card.Root>
					{/each}
				</div>

				{#if vault.error}
					<p class="text-sm font-medium text-destructive">{vault.error}</p>
				{/if}

				<Button
					class="mt-2 w-full cursor-pointer shadow-sm"
					size="lg"
					onclick={async () => vault.upload_files()}
					disabled={vault.uploading}
				>
					{#if vault.uploading}
						<div
							class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground"
						></div>
						Uploading {vault.selected_files.length} files...
					{:else}
						Upload {vault.selected_files.length}
						{vault.selected_files.length === 1 ? 'File' : 'Files'}
					{/if}
				</Button>
			</div>
		{/if}

		<div class="mt-4 flex flex-col gap-4">
			<h2 class="border-b pb-2 text-xl font-bold">Files in Vault</h2>

			{#if vault.server_files.length === 0}
				<div
					class="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/10 py-12 text-center"
				>
					<p class="text-muted-foreground">The vault is currently empty.</p>
				</div>
			{:else}
				<div class="overflow-hidden rounded-xl border">
					<Table.Root>
						<Table.Header class="bg-muted/50">
							<Table.Row>
								<Table.Head>Filename</Table.Head>
								<Table.Head>Size</Table.Head>
								<Table.Head>Author</Table.Head>
								<Table.Head>Date</Table.Head>
								<Table.Head class="text-end">Action</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each vault.server_files as file}
								<Table.Row>
									<Table.Cell class="font-medium">{file.filename}</Table.Cell>
									<Table.Cell class="text-muted-foreground">{format_bytes(file.size)}</Table.Cell>
									<Table.Cell>
										<Badge variant="secondary">{file.uploader}</Badge>
									</Table.Cell>
									<Table.Cell class="text-muted-foreground">
										{new Date(file.upload_date + 'Z').toLocaleDateString()}
									</Table.Cell>
									<Table.Cell class="text-end">
										<div class="flex justify-end gap-2">
											<Button
												variant="outline"
												size="sm"
												class="cursor-pointer"
												onclick={() => vault.trigger_download(file.id, file.filename)}
											>
												<Download class="mr-2" size={14} strokeWidth={2} />
												Download
											</Button>
											<Button
												variant="outline"
												size="sm"
												class="hover:text-destructive-foreground cursor-pointer text-destructive hover:bg-destructive"
												onclick={() => vault.request_delete(file.id, file.filename)}
											>
												<X size={14} strokeWidth={2} />
											</Button>
										</div>
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
						<Table.Footer>
							<Table.Row>
								<Table.Cell colspan={4}>Total Used Storage</Table.Cell>
								<Table.Cell class="text-end">{format_bytes(vault.total_size)}</Table.Cell>
							</Table.Row>
						</Table.Footer>
					</Table.Root>
				</div>
			{/if}
		</div>
	</div>
	<AlertDialog.Root bind:open={vault.is_delete_modal_open}>
		<AlertDialog.Content>
			<AlertDialog.Header>
				<AlertDialog.Title>Are you absolutely sure?</AlertDialog.Title>
				<AlertDialog.Description>
					This action cannot be undone. This will permanently delete the file
					<span class="font-semibold text-foreground">"{vault.file_to_delete?.filename}"</span>
					from the server.
				</AlertDialog.Description>
			</AlertDialog.Header>
			<AlertDialog.Footer>
				<AlertDialog.Cancel onclick={() => (vault.file_to_delete = null)}>
					Cancel
				</AlertDialog.Cancel>
				<AlertDialog.Action
					class="text-destructive-foreground bg-destructive hover:bg-destructive/90"
					onclick={async () => await vault.confirm_delete()}
				>
					Delete File
				</AlertDialog.Action>
			</AlertDialog.Footer>
		</AlertDialog.Content>
	</AlertDialog.Root>
{/if}

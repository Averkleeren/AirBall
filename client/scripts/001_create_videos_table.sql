-- Create videos table for storing uploaded basketball shot videos
create table if not exists public.videos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  file_url text not null,
  status text not null default 'uploaded' check (status in ('uploaded', 'processing', 'analyzed', 'error')),
  shot_score integer,
  arc_angle numeric,
  release_speed numeric,
  follow_through_score integer,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.videos enable row level security;

create policy "videos_select_own" on public.videos for select using (auth.uid() = user_id);
create policy "videos_insert_own" on public.videos for insert with check (auth.uid() = user_id);
create policy "videos_update_own" on public.videos for update using (auth.uid() = user_id);
create policy "videos_delete_own" on public.videos for delete using (auth.uid() = user_id);

-- Schema do Revisional — rode no SQL Editor do Supabase.
-- Modelo: escritório único; todo usuário autenticado enxerga os casos do escritório.
-- IMPORTANTE: desative "Allow new users to sign up" em Authentication > Providers > Email
-- e crie os usuários do escritório manualmente (convite).

create table if not exists public.casos (
  id uuid primary key default gen_random_uuid(),
  criado_por uuid not null default auth.uid() references auth.users(id),
  cliente text not null,
  contrato text,
  banco text,
  dados jsonb not null,        -- parâmetros de entrada do cálculo
  resultado jsonb not null,    -- resumo do resultado (indébito, taxa efetiva etc.)
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists casos_criado_em_idx on public.casos (criado_em desc);
create index if not exists casos_cliente_idx on public.casos (cliente);

create or replace function public.set_atualizado_em()
returns trigger language plpgsql as $$
begin
  new.atualizado_em = now();
  return new;
end $$;

drop trigger if exists casos_set_atualizado_em on public.casos;
create trigger casos_set_atualizado_em
  before update on public.casos
  for each row execute function public.set_atualizado_em();

alter table public.casos enable row level security;

drop policy if exists "casos_select" on public.casos;
drop policy if exists "casos_insert" on public.casos;
drop policy if exists "casos_update" on public.casos;
drop policy if exists "casos_delete" on public.casos;

create policy "casos_select" on public.casos
  for select to authenticated using (true);

create policy "casos_insert" on public.casos
  for insert to authenticated with check (criado_por = auth.uid());

create policy "casos_update" on public.casos
  for update to authenticated using (true) with check (true);

-- Exclusão só pelo autor do caso
create policy "casos_delete" on public.casos
  for delete to authenticated using (criado_por = auth.uid());

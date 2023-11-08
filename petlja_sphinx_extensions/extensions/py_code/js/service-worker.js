addEventListener('install', () => {
    self.skipWaiting();
});
addEventListener('activate', () => {
    self.clients.claim();
});

var resolvers = new Map()

addEventListener('fetch', (event) => {
    const url = new URL(event.request.url)

    if (url.pathname === '/py-get-input/') {
        const id = url.searchParams.get('id')
        const prompt = url.searchParams.get('prompt')

        event.waitUntil(
            (async () => {
                self.clients.matchAll().then((clients) => {
                    clients.forEach((client) => {
                        if (client.type === 'window') {
                            client.postMessage({
                                type: 'PY_AWAITING_INPUT',
                                id,
                                prompt
                            })
                        }
                    })
                })
            })()
        )
        const promise = new Promise((r) => {
            resolvers.set(id, [...(resolvers.get(id) || []), r])
        });
        event.respondWith(promise)
    }
});

addEventListener('message', (event) => {
    if (event.data.type === 'PY_INPUT') {
        const resolverArray = resolvers.get(event.data.id)
        if (!resolverArray || resolverArray.length === 0) {
            console.error('Error handing input: No resolver')
            return
        }
        const resolver = resolverArray.shift() // Take the first promise in the array
        resolver(new Response(event.data.value, { status: 200 }))
    }
});


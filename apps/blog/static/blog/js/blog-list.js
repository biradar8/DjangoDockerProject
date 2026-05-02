document.addEventListener("DOMContentLoaded", function () {
    const trigger = document.getElementById("infinite-scroll-trigger");
    const container = document.getElementById("posts-container");

    if (!trigger || !container) return;

    // -----------------------------
    // State
    // -----------------------------
    let offset = 10;
    const limit = 10;
    let isFetching = false;
    let hasMore = true;

    // -----------------------------
    // Filters
    // -----------------------------
    const urlParams = new URLSearchParams(window.location.search);
    const search = urlParams.get("q") || "";

    const categorySelect = document.getElementById("category-select");
    const categorySlugExact =
        categorySelect?.selectedOptions[0]?.value || null;

    // -----------------------------
    // GraphQL query (static, no dynamic injection)
    // -----------------------------
    const QUERY = `
        query GetAllPosts(
            $limit: Int!,
            $offset: Int!,
            $search: String,
            $categorySlugExact: String
        ) {
          posts(
            pagination: {limit: $limit, offset: $offset}
            filters: {
              title: {iContains: $search},
              category: {slug: {exact: $categorySlugExact}}
            }
          ) {
            id
            title
            titleSlug
            body
            readCreatedAt
            createdBy {
              username
              fullName
            }
            category {
              name
            }
          }
        }
    `;

    // -----------------------------
    // Fetch posts
    // -----------------------------
    async function fetchPosts() {
        if (isFetching || !hasMore) return;
        isFetching = true;

        const variables = {
            limit,
            offset,
            search,
            categorySlugExact: categorySlugExact || null,
        };

        try {
            const res = await fetch("/graphql/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: QUERY,
                    variables,
                }),
            });

            const result = await res.json();
            const posts = result.data?.posts || [];

            if (posts.length === 0) {
                hasMore = false;
                trigger.innerText = "You've reached the end!";
                return;
            }

            renderPosts(posts);

            offset += limit;

            if (posts.length < limit) {
                hasMore = false;
                trigger.innerText = "You've reached the end!";
            }
        } catch (err) {
            console.error("GraphQL fetch failed:", err);
        } finally {
            isFetching = false;
        }
    }
    function postMeta(post) {
        let meta = `By <strong>${escapeHTML(post.createdBy.username)}</strong>`;

        if (post.category) {
            meta += ` • ${escapeHTML(post.category.name)}`;
        }

        if (post.readCreatedAt) {
            meta += ` • ${post.readCreatedAt}`;
        }

        return meta;
    }
    // -----------------------------
    // Post card template
    // IMPORTANT: Must match blog/components/post_card.html
    // -----------------------------
    function postCardTemplate(post, excerpt, url) {
        return html`
        <div class="card mb-4">
            <div class="card-body p-4">

                <h2 class="card-title h5 mb-2">
                    <a href="${url}" class="text-decoration-none text-dark">
                        ${escapeHTML(post.title)}
                    </a>
                </h2>

                <div class="text-muted mb-2 small">
                    ${postMeta(post)}
                </div>

                <p class="card-text text-muted">
                    ${escapeHTML(excerpt)}
                </p>

                <a href="${url}" class="btn btn-sm btn-outline-primary">
                    Read More →
                </a>

            </div>
        </div>
    `;
    }

    // -----------------------------
    // Render posts
    // -----------------------------
    function renderPosts(posts) {
        posts.forEach(post => {
            const temp = document.createElement("div");
            temp.innerHTML = post.body;

            const text = temp.textContent || "";
            const excerpt = text.split(" ").slice(0, 30).join(" ") + "...";

            const url = `/blog/${post.titleSlug}/`;

            const html = postCardTemplate(post, excerpt, url);

            container.insertAdjacentHTML("beforeend", html);
        });
    }

    // -----------------------------
    // Infinite scroll observer
    // -----------------------------
    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
            fetchPosts();
        }
    }, {
        rootMargin: "200px",
    });

    observer.observe(trigger);
});
// -----------------------------
// Helper functions
// -----------------------------
function escapeHTML(str) {
    return str.replace(/[&<>"']/g, tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }[tag]));
}
function html(strings, ...values) {
    return strings.reduce((result, str, i) =>
        result + str + (values[i] || ""), "");
}
function cleanForm(form) {
    const q = form.querySelector("input[name='q']");
    const cat = form.querySelector("select[name='category']");

    if (q && !q.value.trim()) {
        q.removeAttribute("name");
    }

    if (cat && !cat.value) {
        cat.removeAttribute("name");
    }
}

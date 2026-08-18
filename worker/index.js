/**
 * Serwuje zawartosc public/ pod sciezka /claude-code/ na lukaszpodgorski.pl.
 *
 * Pages przypina sie do calej nazwy hosta, a nie do podkatalogu, dlatego strona
 * stoi na Workerze ze statycznymi zasobami: trasa lapie /claude-code/*,
 * prefiks jest zdejmowany, reszta idzie prosto do zasobow.
 */
const PREFIX = "/claude-code";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // bez ukosnika na koncu linki wzgledne w stronie rozjechalyby sie o poziom
    if (url.pathname === PREFIX) {
      return Response.redirect(url.origin + PREFIX + "/", 301);
    }

    const sciezka = url.pathname.startsWith(PREFIX + "/")
      ? url.pathname.slice(PREFIX.length)
      : url.pathname;

    const cel = new URL(sciezka + url.search, url.origin);
    const odp = await env.ASSETS.fetch(new Request(cel, request));

    // zasoby przekierowuja wzgledem sciezki BEZ prefiksu (np. /timeline ->
    // /timeline/), wiec trzeba go doklejac z powrotem, inaczej uzytkownik
    // ladowalby poza /claude-code/ i trafial na stary origin
    const cel2 = odp.headers.get("location");
    if (cel2 && cel2.startsWith("/") && !cel2.startsWith(PREFIX + "/")) {
      const poprawiona = new Response(odp.body, odp);
      poprawiona.headers.set("location", PREFIX + cel2);
      return poprawiona;
    }
    return odp;
  },
};

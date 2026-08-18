/**
 * Serwuje strone pod sciezka /claude-code/ na lukaszpodgorski.pl.
 *
 * Ten Worker nie ma zadnych plikow. Cloudflare nie pozwala kierowac Workera ze
 * statycznymi zasobami na trase zawierajaca sciezke (tylko na cala nazwe hosta),
 * a strona ma stac pod /claude-code/ na domenie, ktorej korzen obsluguje PHP.
 * Dlatego pliki trzyma osobny Worker `claude-code-assets`, wolany tutaj przez
 * wiazanie uslugowe SITE. Ruch nie wychodzi przy tym poza siec Cloudflare.
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
    const odp = await env.SITE.fetch(new Request(cel, request));

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

/**
 * Worker trzymajacy pliki strony. Nie ma zadnej trasy na domenie: siega po niego
 * wylacznie Worker `claude-code` przez wiazanie uslugowe.
 *
 * Podzial na dwa Workery jest wymuszony przez Cloudflare: Worker ze statycznymi
 * zasobami nie moze byc podpiety pod trase ze sciezka (tylko pod cala nazwe hosta),
 * a strona ma stac pod /claude-code/ na domenie, ktorej korzen obsluguje co innego.
 */
export default {
  fetch(request, env) {
    return env.ASSETS.fetch(request);
  },
};
